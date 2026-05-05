from __future__ import annotations

import json
import os
import hashlib
from contextlib import contextmanager

from config import SAVE_FILE
from errors import SaveError, StateError, safe_action, handle_error
from logger import log_event


_last_saved_digest: str | None = None


@contextmanager
def safe_file(label: str):
    try:
        yield

    except (OSError, json.JSONDecodeError) as e:
        raise SaveError(f"{label} — {e}") from e


def compute_hash(data_bytes: bytes) -> str:
    h = hashlib.sha256()
    h.update(data_bytes)
    return h.hexdigest()


@safe_action
def save_game(state: dict, *, force: bool = False) -> None:
    """Write state to disk with SHA-256 integrity hash."""
    global _last_saved_digest

    with safe_file("saving game"):
        payload = json.dumps(state, sort_keys=True).encode("utf-8")
        digest = compute_hash(payload)

        if not force and digest == _last_saved_digest and os.path.exists(SAVE_FILE):
            return

        wrapper = {
            "state": state,
            "hash": digest
        }

        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(wrapper, f, indent=2)

        _last_saved_digest = digest

    log_event("SAVE_ATTEMPT", f"File={SAVE_FILE}", "SUCCESS")
    print("  [Progress saved.]")


def load_game() -> dict | None:
    """Return verified save state, or None on failure."""
    global _last_saved_digest

    if not os.path.exists(SAVE_FILE):
        log_event("LOAD_ATTEMPT", "No save file found", "FAIL")
        print("  No save file found.")
        return None

    try:
        with safe_file("loading save"):
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                wrapper = json.load(f)

        state = wrapper.get("state")
        saved_hash = wrapper.get("hash")

        if state is None or saved_hash is None:
            raise StateError("Save file is missing state or hash field.")

        payload = json.dumps(state, sort_keys=True).encode("utf-8")

        if compute_hash(payload) != saved_hash:
            raise StateError("Hash mismatch — save file may have been tampered with.")

        required = {"inventory", "location", "flags", "story_progress"}

        if not required.issubset(state.keys()):
            raise StateError("Save file is missing required game-state fields.")

        # Keeps old saves compatible if they were made before scene_step existed.
        state.setdefault("scene_step", state.get("location", "start"))

        _last_saved_digest = saved_hash

        log_event("LOAD_ATTEMPT", f"File={SAVE_FILE}", "SUCCESS")
        print("  [Game loaded successfully.]")

        return state

    except (SaveError, StateError) as e:
        handle_error(e)
        log_event("LOAD_ATTEMPT", str(e), "FAIL")
        return None


@safe_action
def delete_save() -> None:
    global _last_saved_digest

    with safe_file("deleting save"):
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)

        _last_saved_digest = None
