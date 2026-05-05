def default_state() -> dict:
    return {
        "inventory": [],
        "location": "start",
        "scene_step": "start",
        "flags": {},
        "story_progress": []
    }


def reset_state(state: dict) -> None:
    """Reset the current in-memory state without replacing the dictionary object."""
    state.clear()
    state.update(default_state())