"""
USS Smenterprise — Text Adventure
=======================================================
    A text adventure game built around choices and the consequences of the choice made either bad or good.
"""

import random
import json
import hashlib
import datetime
import os
import sys
import functools
from contextlib import contextmanager

SAVE_FILE  = "savegame.json"
AUDIT_LOG  = "audit_log.txt"


# ══════════════════════════════════════════════════════════════════
#  LAYER 1 — CUSTOM EXCEPTION HIERARCHY
#  ─────────────────────────────────────────────────────────────────
#  Every error in the game is one of these types.
#  Catch GameError for anything; catch a subclass to target one area.
# ══════════════════════════════════════════════════════════════════

class GameError(Exception):
    """Base — catches any game-layer error."""

class InputError(GameError):
    """Player input was invalid or the input stream closed."""

class SaveError(GameError):
    """A save / load / delete file operation failed."""

class StateError(GameError):
    """Game state is missing required keys or is otherwise corrupt."""


# ══════════════════════════════════════════════════════════════════
#  LAYER 2 — CENTRAL ERROR REPORTER  handle_error()
#  ─────────────────────────────────────────────────────────────────
#  One function decides how every error is displayed.
#  Edit only this function to change formatting across the whole game.
# ══════════════════════════════════════════════════════════════════

def handle_error(error: Exception, *, fatal: bool = False) -> None:
    tag = "FATAL" if fatal else "WARNING"
    print(f"\n  [{tag} — {type(error).__name__}]: {error}\n")
    log_event("ERROR", f"{type(error).__name__}: {error}", "FATAL" if fatal else "WARNING")
    if fatal:
        print("  Your progress was saved at the last checkpoint.")
        sys.exit(1)


# ══════════════════════════════════════════════════════════════════
#  LAYER 3 — @safe_action DECORATOR
#  ─────────────────────────────────────────────────────────────────
#  Apply to any game function — it will never crash the interpreter.
#  GameErrors are caught non-fatally; unexpected Exceptions are fatal.
#
#  Usage:
#      @safe_action
#      def some_scene(state): ...
# ══════════════════════════════════════════════════════════════════

def safe_action(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print("\n\n  Interrupted — exiting. Progress saved at last checkpoint.")
            log_event("GAME_END", "KeyboardInterrupt", "EXIT")
            sys.exit(0)
        except GameError as e:
            handle_error(e)
        except Exception as e:
            handle_error(e, fatal=True)
    return wrapper


# ══════════════════════════════════════════════════════════════════
#  LAYER 4 — safe_file() CONTEXT MANAGER
#  ─────────────────────────────────────────────────────────────────
#  Wrap every file operation here.
#  Translates OSError / JSONDecodeError → SaveError so callers only
#  ever handle one exception type for I/O.
#
#  Usage:
#      with safe_file("saving game"):
#          with open(SAVE_FILE, "w") as f:
#              json.dump(state, f)
# ══════════════════════════════════════════════════════════════════

@contextmanager
def safe_file(label: str):
    try:
        yield
    except (OSError, json.JSONDecodeError) as e:
        raise SaveError(f"{label} — {e}") from e


# ══════════════════════════════════════════════════════════════════
#  LAYER 5 — INPUT VALIDATORS
#  ─────────────────────────────────────────────────────────────────
#   get_input          — loops until player types a valid option
#   prompt_menu_number — loops until player types a number in range
#   Both raise InputError on EOF; KeyboardInterrupt bubbles to @safe_action
# ══════════════════════════════════════════════════════════════════

def get_input(prompt: str, valid: list[str]) -> str:
    valid_lower = [v.lower() for v in valid]
    display     = " / ".join(valid)
    while True:
        try:
            raw = input(prompt).strip().lower()
        except EOFError:
            raise InputError(f"Input stream closed — expected one of: {display}")
        if raw in valid_lower:
            return raw
        log_event("INPUT_INVALID", f'Got "{raw}" — expected one of: {display}')
        print(f"  [Invalid input '{raw}'. Please enter one of: {display}]")


def prompt_menu_number(prompt: str, min_val: int, max_val: int) -> int:
    while True:
        try:
            raw = input(prompt).strip()
            num = int(raw)
            if min_val <= num <= max_val:
                return num
            log_event("INPUT_INVALID", f'Got "{raw}" — expected {min_val}–{max_val}')
            print(f"  [Please enter a number from {min_val} to {max_val}.]")
        except ValueError:
            log_event("INPUT_INVALID", f'Non-integer "{raw}" at numeric menu')
            print(f"  [Please enter a number from {min_val} to {max_val}.]")
        except EOFError:
            raise InputError("Input stream closed at menu.")

# ══════════════════════════════════════════════════════════════════════════════
# Filing Logic
# ══════════════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════
#  Audit Log

def log_event(event_type: str, message: str = "", result: str = "") -> None:
    """Append a timestamped line to the audit log. Never raises — silent on failure."""
    try:
        ts    = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        parts = [ts, "-", event_type]
        if result:
            parts += ["-", result]
        if message:
            parts += ["-", message]
        with open(AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(" ".join(parts) + "\n")
    except OSError:
        pass  # audit failure must never interrupt gameplay


# ══════════════════════════════════════════════════════════════════
#  Save / Load 

def compute_hash(data_bytes: bytes) -> str:
    h = hashlib.sha256()
    h.update(data_bytes)
    return h.hexdigest()


@safe_action
def save_game(state: dict) -> None:
    """Write state to disk with SHA-256 integrity hash."""
    with safe_file("saving game"):
        payload = json.dumps(state, sort_keys=True).encode("utf-8")
        digest  = compute_hash(payload)
        wrapper = {"state": state, "hash": digest}
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(wrapper, f, indent=2)
    log_event("SAVE_ATTEMPT", f"File={SAVE_FILE}", "SUCCESS")
    print("  [Progress saved.]")


def load_game() -> dict | None:
    """Return verified save state, or None on any failure."""
    if not os.path.exists(SAVE_FILE):
        log_event("LOAD_ATTEMPT", "No save file found", "FAIL")
        print("  No save file found.")
        return None
    try:
        with safe_file("loading save"):
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                wrapper = json.load(f)

        state      = wrapper.get("state")
        saved_hash = wrapper.get("hash")

        if state is None or saved_hash is None:
            raise StateError("Save file is missing state or hash field.")

        # Integrity check — detect tampering
        payload = json.dumps(state, sort_keys=True).encode("utf-8")
        if compute_hash(payload) != saved_hash:
            raise StateError("Hash mismatch — save file may have been tampered with.")

        required = {"inventory", "location", "flags", "story_progress"}
        if not required.issubset(state.keys()):
            raise StateError("Save file is missing required game-state fields.")

        log_event("LOAD_ATTEMPT", f"File={SAVE_FILE}", "SUCCESS")
        print("  [Game loaded successfully.]")
        return state

    except (SaveError, StateError) as e:
        handle_error(e)            # warn but don't crash
        log_event("LOAD_ATTEMPT", str(e), "FAIL")
        return None


@safe_action
def delete_save() -> None:
    with safe_file("deleting save"):
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)

# ══════════════════════════════════════════════════════════════════════════════
# Core Game Structures
# ══════════════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════
#  Default Sate

def default_state() -> dict:
    return {
        "inventory":      [],
        "location":       "start",
        "flags":          {},
        "story_progress": []
    }


# ══════════════════════════════════════════════════════════════════
#  Inventory Helper

def add_item(state: dict, item: str) -> None:
    if item not in state["inventory"]:
        state["inventory"].append(item)
        log_event("ITEM_ACQUIRED", f"Item={item}")
        print(f"  You acquired: {item}")
    else:
        print(f"  You already have: {item}")


def remove_item(state: dict, item: str) -> bool:
    if item in state["inventory"]:
        state["inventory"].remove(item)
        log_event("ITEM_REMOVED", f"Item={item}")
        print(f"  You used/removed: {item}")
        return True
    return False


def show_inventory(state: dict) -> None:
    inv = state["inventory"]
    print("  Inventory:", ", ".join(inv) if inv else "(empty)")
    print("  Location :", state.get("location", "unknown"))
    active = {k: v for k, v in state.get("flags", {}).items() if v}
    if active:
        print("  Status   :", ", ".join(f"{k}={v}" for k, v in active.items()))


# ══════════════════════════════════════════════════════════════════
#  NPC System 

NPCS: dict = {
    "smock": {
        "where":    "bridge",
        "role":     "advisor",
        "dialogue": [
            'Smock: "It is Smarfleet\'s policy to render aid to anyone in need."',
            'Smock: "Check the terminal for access codes."'
        ],
        "gives": ["HintToken"]
    },
    "haru": {
        "where":    "colony_house",
        "role":     "engineer",
        "dialogue": [
            'Haru: "I can help repair systems if you bring me a schematic."',
            'Haru: "With the schematic we can reprogram the replicator."'
        ],
        "gives": []
    },
    "mira": {
        "where":    "disabled_ship",
        "role":     "scientist",
        "dialogue": [
            'Mira: "My lab notes contain a code fragment. I will trade for a coin."',
            'Mira: "Take this access code if you help me secure the core."'
        ],
        "gives": ["AccessCode"]
    },
    "guard": {
        "where":    "loading_bay",
        "role":     "gatekeeper",
        "dialogue": [
            'Guard: "You need a keycard to pass."',
            'Guard: "If you can prove you\'re not a threat, I\'ll let you through."'
        ],
        "gives": []
    },
    "trader": {
        "where":    "market",
        "role":     "merchant",
        "dialogue": [
            'Trader: "I trade useful things for trinkets."',
            'Trader: "Coins are valuable here."'
        ],
        "gives": ["MedPatch"]
    }
}

NPC_KEYS = list(NPCS.keys())


@safe_action
def talk_to_npc(state: dict, npc_key: str) -> None:
    npc = NPCS.get(npc_key)
    if not npc:
        print(f"  No one here by the name '{npc_key}'.")
        return

    print()
    for line in npc["dialogue"]:
        print(" ", line)

    # Trade logic
    if npc_key == "mira":
        if "Coin" in state["inventory"]:
            if get_input("\n  Trade your Coin for an AccessCode? (y/n): ", ["y", "n"]) == "y":
                remove_item(state, "Coin")
                add_item(state, "AccessCode")
                log_event("NPC_TRADE", "NPC=Mira Coin->AccessCode", "SUCCESS")
        else:
            print("  You don't have a coin to trade.")

    elif npc_key == "trader":
        if "Coin" in state["inventory"]:
            if get_input("\n  Trade your Coin for a MedPatch? (y/n): ", ["y", "n"]) == "y":
                remove_item(state, "Coin")
                add_item(state, "MedPatch")
                log_event("NPC_TRADE", "NPC=Trader Coin->MedPatch", "SUCCESS")
        else:
            print('  Trader: "Come back with a coin."')

    elif npc_key == "smock":
        if "HintToken" not in state["inventory"]:
            add_item(state, "HintToken")

    save_game(state)


# ══════════════════════════════════════════════════════════════════
#  Mini Games 

@safe_action
def terminal_puzzle(state: dict) -> bool:
    """
    Guess a 3-letter code in 3 attempts.
    Returns True on success, False on failure.
    Input is validated: must be exactly 3 alphabetic characters.
    """
    secret   = random.choice(["zen", "ark", "ion", "sol", "tau"])
    attempts = 3
    log_event("CHALLENGE_ATTEMPT", "Puzzle=TerminalLogin START")

    for i in range(1, attempts + 1):
        # Validate: loop until player enters exactly 3 alpha chars
        while True:
            try:
                raw = input(f"\n  Terminal login {i}/{attempts} — enter 3-letter code: ").strip().lower()
            except EOFError:
                raise InputError("Input stream closed during terminal puzzle.")
            if len(raw) == 3 and raw.isalpha():
                break
            print("  [Code must be exactly 3 letters, e.g. 'ark']")
            log_event("INPUT_INVALID", f'Terminal puzzle got "{raw}"')

        if raw == secret:
            print("  Access granted. You disabled an alarm zone.")
            log_event("CHALLENGE_ATTEMPT", "Puzzle=TerminalLogin", "SUCCESS")
            state["flags"]["alarm_disabled"] = True
            return True

        # Build letter-by-letter hint
        hint = []
        for a, b in zip(raw, secret):
            hint.append("✓" if a == b else ("~" if a in secret else "✗"))
        print("  Hint:", " ".join(hint), "  (✓=correct  ~=wrong position  ✗=not in code)")
        log_event("CHALLENGE_ATTEMPT", f"Puzzle=TerminalLogin FAIL attempt={i}")

    print("  Terminal locked. A security sweep has been triggered.")
    log_event("CHALLENGE_ATTEMPT", "Puzzle=TerminalLogin", "FAIL")
    state["flags"]["sweep_triggered"] = True
    return False


@safe_action
def corridor_encounter(state: dict) -> bool:
    """Drone encounter — fight, distract, or run."""
    print("\n  A hostile drone blocks your path.")
    log_event("CHALLENGE_ATTEMPT", "Encounter=Drone START")
    choice = get_input("  Do you fight, distract, or run? (fight/distract/run): ",
                       ["fight", "distract", "run"])

    if choice == "fight":
        power = 0.5 + (0.2 if "Coin" in state["inventory"] else 0)
        if random.random() < power:
            print("  You disabled the drone.")
            log_event("CHALLENGE_ATTEMPT", "Encounter=Drone", "SUCCESS")
            return True
        print("  The drone damages you and you retreat.")
        log_event("CHALLENGE_ATTEMPT", "Encounter=Drone", "FAIL")
        state["flags"]["injured"] = True
        return False

    elif choice == "distract":
        if "Apple" in state["inventory"]:
            print("  You toss the apple — the drone tracks it and you slip past.")
            remove_item(state, "Apple")
            log_event("CHALLENGE_ATTEMPT", "Encounter=Drone", "SUCCESS")
            return True
        print("  Nothing to distract it with. It attacks.")
        log_event("CHALLENGE_ATTEMPT", "Encounter=Drone", "FAIL")
        state["flags"]["injured"] = True
        return False

    else:  # run
        if random.random() < 0.6:
            print("  You outrun the drone.")
            log_event("CHALLENGE_ATTEMPT", "Encounter=Drone", "SUCCESS")
            return True
        print("  You fail to escape and are injured.")
        log_event("CHALLENGE_ATTEMPT", "Encounter=Drone", "FAIL")
        state["flags"]["injured"] = True
        return False


# ══════════════════════════════════════════════════════════════════
#  Start of the Game
# ══════════════════════════════════════════════════════════════════

@safe_action
def print_intro(state: dict) -> None:
    print("""
  Star date 74219.6

  The stars hang silent beyond the viewport of the USS Smenterprise, their
  light stretched thin across the cold expanse of the Neutral Zone. For nearly
  a century, the Federation and the Klingon Star Empire have maintained an uneasy
  stillness here — neither war, nor peace — only distance.

  Until now.

  A distortion tears through subspace like a wound reopening. Sensors aboard the
  Smenterprise shudder as a signal cuts through the static — fragmented, repeating,
  urgent.

    "This is.. unidentified vessel... repeating distress — drifting... we are not...
     please respond — location unstable... hull integrity failing. End transmission."
""")
    log_event("GAME_START", "Player started a new game")
    state["location"] = "bridge"
    save_game(state)


# ══════════════════════════════════════════════════════════════════
# BRIDGE

@safe_action
def start_bridge(state: dict) -> None:
    print("\n  You are on the bridge. Smock stands at the science station.")
    choice = get_input(
        "  Talk to Smock, check the console, or leave the bridge? (talk/console/leave): ",
        ["talk", "console", "leave"]
    )

    if choice == "talk":
        talk_to_npc(state, "smock")
        # Give player a chance to act after consulting Smock
        start_bridge(state)

    elif choice == "console":
        print("\n  Console shows two contacts in the Neutral Zone:")
        print("    (c) Colony ship  — aged, very low power readings")
        print("    (d) Disabled ship — warp core breach, worsening fast")
        sel = get_input("  Which do you approach? (c/d): ", ["c", "d"])
        if sel == "c":
            state["location"] = "colony_ship"
            log_event("CHOICE_MADE", "Selected=ColonyShip")
            save_game(state)
            colony_ship_scene(state)
        else:
            state["location"] = "disabled_ship"
            log_event("CHOICE_MADE", "Selected=DisabledShip")
            save_game(state)
            disabled_ship_scene(state)

    else:
        print("  You leave the bridge and head down the main corridor.")
        state["location"] = "corridor"
        save_game(state)
        corridor_scene(state)


# ══════════════════════════════════════════════════════════════════
# CORRIDOR

@safe_action
def corridor_scene(state: dict) -> None:
    print("\n  Corridor: you notice an apple sitting on a crate.")
    if get_input("  Pick it up? (y/n): ", ["y", "n"]) == "y":
        add_item(state, "Apple")
        save_game(state)

    print("\n  A coin glints near a ventilation grate.")
    if get_input("  Pick it up? (y/n): ", ["y", "n"]) == "y":
        add_item(state, "Coin")
        save_game(state)

    # Random encounter
    if random.random() < 0.4:
        corridor_encounter(state)
        save_game(state)

    print("\n  You reach a junction with a map terminal.")
    action = get_input("  Open the map, check inventory, or go back to the bridge? (map/inv/back): ",
                       ["map", "inv", "back"])
    if action == "map":
        print("  Map: colony ship to port — disabled ship to starboard.")
    elif action == "inv":
        show_inventory(state)
    else:
        state["location"] = "bridge"
        save_game(state)
        start_bridge(state)


# ══════════════════════════════════════════════════════════════════
# COLONY SHIP

@safe_action
def colony_ship_scene(state: dict) -> None:
    print("""
  You come across a massive generational ship — clearly aged and in disrepair,
  with extremely low energy readings. It's been out here a long, long time.""")

    # Communicate / teleport loop
    while True:
        action = get_input(
            "\n  Attempt to communicate or teleport aboard? (c/t): ", ["c", "t"]
        )
        if action == "t":
            break
        if "Schematic" not in state["inventory"]:
            if random.random() < 0.5:
                print("  A deep scan cuts through the interference — you receive a "
                      "full schematic of the ship.")
                add_item(state, "Schematic")
                save_game(state)
            else:
                print("  You receive no response.")
        else:
            print("  You receive no response.")

    print("""
  You materialise inside a massive habitat-like structure — an Earth-like
  atmosphere, a simulated day-night cycle. It's breathtaking.""")

    # Scan / look loop
    while True:
        action = get_input(
            "\n  Look around or scan for life forms? (look/scan): ", ["look", "scan"]
        )
        if action == "scan":
            break
        print("  You explore but find nothing immediately useful.")

    print("  Thousands of humanoid life forms detected. There is a house nearby.")

    # Find Haru
    approach = get_input(
        "\n  Search for inhabitants or look for the ship's engineer? (search/engineer): ",
        ["search", "engineer"]
    )
    if approach == "engineer":
        talk_to_npc(state, "haru")
    else:
        print("  You find a house — someone answers the door. It's an engineer named Haru.")
        talk_to_npc(state, "haru")

    print("\n  You discover these people have no idea they are in space — or that "
          "their ship is failing.")

    # Repair decision
    if "Schematic" in state["inventory"]:
        print("\n  You show Haru the schematic. The truth settles over the colony "
              "like a cold wave — they are in space, and their ship is dying.")
        print("  Back on the Smenterprise the replicator is on the fritz. "
              "You attempt to fabricate parts.")

        choice = get_input(
            "\n  Attempt repairs yourself or teach them to do it? (self/teach): ",
            ["self", "teach"]
        )
        if choice == "self":
            chance = 0.9 if "Coin" in state["inventory"] else 0.7
            if random.random() < chance:
                print("\n  Every component fabricated. The colony ship is restored to "
                      "factory condition in record time. The colonists are grateful.\n\n"
                      "  ★  VICTORY — Colony Saved  ★")
                log_event("ENDING", "ColonyRepair", "SUCCESS")
                state["flags"]["ending"] = "ColonyRepair"
            else:
                print("\n  The replicator failed on one critical part. You scavenged "
                      "both ships and got things to mostly working order.\n\n"
                      "  ★  VICTORY — Colony Partially Repaired  ★")
                log_event("ENDING", "ColonyRepairPartial", "SUCCESS")
                state["flags"]["ending"] = "ColonyRepairPartial"
        else:
            print("\n  You walk Haru through every system. The colonists take over "
                  "repairs and succeed — on their own terms.\n\n"
                  "  ★  VICTORY — Colony Self-Sufficient  ★")
            log_event("ENDING", "ColonyTaught", "SUCCESS")
            state["flags"]["ending"] = "ColonyTaught"
    else:
        print("\n  Without a schematic you can't complete repairs. You head back to "
              "search for more resources.")
        log_event("CHOICE_MADE", "Colony_NoSchematic")
        state["location"] = "bridge"
        save_game(state)
        return

    save_game(state)
    delete_save()
    print("\n  [Save data cleared. Thanks for playing!]")


# ══════════════════════════════════════════════════════════════════
# DISABLED SHIP

@safe_action
def disabled_ship_scene(state: dict) -> None:
    print("\n  You board the disabled ship. The warp core breach pulses on your "
          "sensors like a countdown.")

    talk_to_npc(state, "mira")

    if "AccessCode" in state["inventory"]:
        print("\n  Mira's access code fragment helps with the terminal.")
        success = terminal_puzzle(state)
    else:
        print("\n  Without an access code the terminal is at full difficulty.")
        success = terminal_puzzle(state)

    if success:
        print("\n  You stabilise the core and escape through the security checkpoint.\n\n"
              "  ★  VICTORY — Core Stabilized  ★")
        log_event("ENDING", "CoreStabilized", "SUCCESS")
        state["flags"]["ending"] = "CoreStabilized"
    else:
        print("\n  You failed to stabilise the core. You escape through maintenance tunnels.\n\n"
              "  ★  ENDING — Maintenance Escape  ★")
        log_event("ENDING", "MaintenanceEscape", "SUCCESS")
        state["flags"]["ending"] = "MaintenanceEscape"

    save_game(state)
    delete_save()
    print("\n  [Save data cleared. Thanks for playing!]")


# ══════════════════════════════════════════════════════════════════
#  MAIN MENU  (AMY's numbered menu — all 7 options fully functional)
# ══════════════════════════════════════════════════════════════════

def _check_game_started(state: dict, option_name: str) -> bool:
    """Return False and print a warning if the player hasn't started a game yet."""
    if state["location"] == "start":
        print(f"  [Start a new game first before using '{option_name}'.]")
        return False
    return True


def _check_game_over(state: dict) -> bool:
    """Return True (and print a message) if the current run has already ended."""
    if state["flags"].get("ending"):
        ending = state["flags"]["ending"]
        print(f"\n  This run has already ended (outcome: {ending}).")
        print("  Start a new game (option 1) to play again.")
        return True
    return False


def main() -> None:
    state = default_state()
    log_event("GAME_START", "Launcher started")

    print("=" * 60)
    print("        USS SMENTERPRISE  —  TEXT ADVENTURE")
    print("=" * 60)

    while True:
        print("""
  ┌─ Main Menu ───────────────────────────────────┐
  │  1. Start New Game                            │
  │  2. Load Game                                 │
  │  3. Save Game                                 │
  │  4. Check Inventory & Status                  │
  │  5. Explore (continue story)                  │
  │  6. Talk to NPC                               │
  │  7. Quit                                      │
  └───────────────────────────────────────────────┘""")

        choice = prompt_menu_number("  Enter a number (1–7): ", 1, 7)

        # ── 1. Start New Game ─────────────────────────────────────
        if choice == 1:
            if state["location"] != "start":
                confirm = get_input(
                    "  You have a game in progress. Start over? (y/n): ", ["y", "n"]
                )
                if confirm == "n":
                    continue
                delete_save()
            state = default_state()
            print_intro(state)
            start_bridge(state)

        # ── 2. Load Game ──────────────────────────────────────────
        elif choice == 2:
            loaded = load_game()
            if loaded:
                state = loaded
                print(f"  Resumed at location: {state['location']}")
                show_inventory(state)

        # ── 3. Save Game ──────────────────────────────────────────
        elif choice == 3:
            if not _check_game_started(state, "Save Game"):
                continue
            if _check_game_over(state):
                continue
            save_game(state)

        # ── 4. Check Inventory & Status ───────────────────────────
        elif choice == 4:
            if not _check_game_started(state, "Check Inventory"):
                continue
            show_inventory(state)

        # ── 5. Explore ────────────────────────────────────────────
        elif choice == 5:
            if not _check_game_started(state, "Explore"):
                continue
            if _check_game_over(state):
                continue
            loc = state["location"]
            if loc in ("start", "bridge"):
                start_bridge(state)
            elif loc == "corridor":
                corridor_scene(state)
            elif loc == "colony_ship":
                colony_ship_scene(state)
            elif loc == "disabled_ship":
                disabled_ship_scene(state)
            else:
                # Unknown location — fall back to bridge safely
                print(f"  [Unknown location '{loc}' — returning to bridge.]")
                log_event("STATE_WARN", f"Unknown location={loc} — fallback to bridge")
                state["location"] = "bridge"
                save_game(state)
                start_bridge(state)

        # ── 6. Talk to NPC ────────────────────────────────────────
        elif choice == 6:
            if not _check_game_started(state, "Talk to NPC"):
                continue
            if _check_game_over(state):
                continue
            print(f"  NPCs available: {', '.join(NPC_KEYS)}")
            npc_name = get_input(
                "  Who do you want to talk to? ",
                NPC_KEYS          # validated against the actual NPC keys
            )
            talk_to_npc(state, npc_name)

        # ── 7. Quit ───────────────────────────────────────────────
        elif choice == 7:
            if state["location"] != "start" and not state["flags"].get("ending"):
                confirm = get_input(
                    "  Save before quitting? (y/n): ", ["y", "n"]
                )
                if confirm == "y":
                    save_game(state)
            log_event("GAME_END", "Player quit", "SUCCESS")
            print("  Goodbye, Captain.\n")
            break


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        handle_error(e, fatal=True)
