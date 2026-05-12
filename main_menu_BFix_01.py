# Global 'menu' escape
import builtins as _builtins
_real_input = _builtins.input       

class MenuRequested(BaseException):
    """Raised whenever the player types 'menu' at any input prompt."""
def _menu_aware_input(prompt=""):
    value = _real_input(prompt)
    if value.strip().lower() == "menu":
        raise MenuRequested()
    return value

_builtins.input = _menu_aware_input 
# Import structures
from state import default_state
from logger import log_event
from errors import handle_error
from input_helpers import get_input, prompt_menu_number
from inventory import show_inventory
from save_system import save_game, load_game, delete_save
from scenes import (
    print_intro,
    start_bridge,
    corridor_scene,
    colony_ship_scene,
    disabled_ship_arrival_scene,
    disabled_ship_scene,
    disabled_ship_combat_scene
)


def _check_game_started(state: dict, option_name: str) -> bool:
    if state["location"] == "start":
        print(f"  [Start a new game first before using '{option_name}'.]")
        return False

    return True


def _check_game_over(state: dict) -> bool:
    if state["flags"].get("ending"):
        ending = state["flags"]["ending"]

        print(f"\n  This run has already ended (outcome: {ending}).")
        print("  Start a new game (option 1) to play again.")

        return True

    return False


def explore_location(state: dict) -> None:
    loc = state["location"]

    if loc in ("start", "bridge"):
        start_bridge(state)

    elif loc == "corridor":
        corridor_scene(state)

    elif loc == "colony_ship":
        colony_ship_scene(state)
        
    elif loc == "outside_ship":
        disabled_ship_arrival_scene(state)

    elif loc == "disabled_ship":
        disabled_ship_scene(state)
    
    elif loc == "smenterprise_bridge":
        disabled_ship_combat_scene(state)

    else:
        print(f"  [Unknown location '{loc}' — returning to bridge.]")
        log_event("STATE_WARN", f"Unknown location={loc} — fallback to bridge")

        state["location"] = "bridge"
        state["scene_step"] = "bridge_choice"

        save_game(state)
        start_bridge(state)


def _handle_menu_escape(state: dict) -> bool:
    """
    Called when the player types 'menu' mid-game.
    Returns True  → go to main menu (show it).
    Returns False → resume gameplay from last checkpoint.
    """
    answer = _real_input("\n  Do you wish to go to the main menu? (y/n): ").strip().lower()

    if answer == "y":
        if state["location"] != "start" and not state["flags"].get("ending"):
            save_game(state)
            print("  Progress saved. Returning to main menu…")
        else:
            print("  Returning to main menu…")
        return True
    else:
        print("  Resuming from last checkpoint…")
        return False


def main() -> None:
    state = default_state()

    log_event("GAME_START", "Launcher started")

    print("=" * 60)
    print("        USS SMENTERPRISE  —  TEXT ADVENTURE")
    print("=" * 60)

    while True:
        print("""
              
              --- Type "menu" to get back here ---           
  ┌─ Main Menu ───────────────────────────────────┐
  │  1. Start New Game                            │
  │  2. Load Game                                 │
  │  3. Save Game                                 │
  │  4. Check Inventory & Status                  │
  │  5. Explore (continue story)                  │
  │  6. Quit                                      │
  └───────────────────────────────────────────────┘""")

        try:
            choice = prompt_menu_number("  Enter a number (1–6): ", 1, 6)

            if choice == 1:
                if state["location"] != "start":
                    confirm = get_input(
                        "  You have a game in progress. Start over? (y/n): ",
                        ["y", "n"]
                    )

                    if confirm == "n":
                        continue

                    delete_save()

                state = default_state()
                print_intro(state)
                start_bridge(state)

            elif choice == 2:
                loaded = load_game()

                if loaded:
                    state = loaded

                    print(f"  Resumed at location: {state['location']}")
                    print(f"  Story step: {state.get('scene_step', 'unknown')}")

                    show_inventory(state)

            elif choice == 3:
                if not _check_game_started(state, "Save Game"):
                    continue

                if _check_game_over(state):
                    continue

                save_game(state, force=True)

            elif choice == 4:
                if not _check_game_started(state, "Check Inventory"):
                    continue

                show_inventory(state)

            elif choice == 5:
                if not _check_game_started(state, "Explore"):
                    continue

                if _check_game_over(state):
                    continue

                explore_location(state)

            elif choice == 6:
                if state["location"] != "start" and not state["flags"].get("ending"):
                    confirm = get_input("  Save before quitting? (y/n): ", ["y", "n"])

                    if confirm == "y":
                        save_game(state, force=True)

                log_event("GAME_END", "Player quit", "SUCCESS")
                print("  Goodbye, Captain.\n")

                break

        except MenuRequested:
            try:
                go_to_menu = _handle_menu_escape(state)
            except MenuRequested:
                go_to_menu = True
            if not go_to_menu and state["location"] != "start":
                explore_location(state)


if __name__ == "__main__":
    try:
        main()

    except MenuRequested:
        pass 

    except Exception as e:
        handle_error(e, fatal=True)
