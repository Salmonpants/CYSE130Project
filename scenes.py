import random

from errors import safe_action
from input_helpers import get_input
from inventory import add_item, remove_item, show_inventory
from save_system import save_game, delete_save
from logger import log_event
from npcs import talk_to_npc
from minigames import terminal_puzzle, corridor_encounter
from state import reset_state


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
    state["scene_step"] = "bridge_choice"

    save_game(state)

# --------------------------------------
#  Bridge

@safe_action
def start_bridge(state: dict) -> None:
    state["location"] = "bridge"
    state["scene_step"] = "bridge_choice"
    save_game(state)

    print("\n  You are on the bridge. Smock stands at the science station.")

    choice = get_input(
        "  Talk to Smock, check the console, or leave the bridge? (talk/console/leave): ",
        ["talk", "console", "leave"]
    )

    if choice == "talk":
        talk_to_npc(state, "smock", add_item, remove_item, get_input, log_event)
        save_game(state)
        start_bridge(state)

    elif choice == "console":
        state["scene_step"] = "bridge_console_choice"
        save_game(state)

        print("\n  Console shows two contacts in the Neutral Zone:")
        print("    (c) Colony ship  — aged, very low power readings")
        print("    (d) Disabled ship — warp core breach, worsening fast")
        print("    (i) Ignore - The situation there is unstable")

        sel = get_input("  Which do you approach? (c/d/i): ", ["c", "d","i"])

        if sel == "c":
            state["location"] = "colony_ship"
            state["scene_step"] = "colony_start"
            log_event("CHOICE_MADE", "Selected=ColonyShip")
            colony_ship_scene(state)
            
        elif choice == "i":
            print("In the light of pollitical unrest you decided to leave and ignore those calls")
            print("When you get back home you are met with a chapter out of smarfleet")
            print("as you have been in breach of smarfeets core values")
            log_event("ENDING", "Ignored calls for help", "SUCCESS")
            state["flags"]["ending"] = "Ignored calls for help"
            delete_save()
            reset_state(state)
            print("\n  [Save data cleared. Thanks for playing!]")

        else:
            state["location"] = "disabled_ship"
            state["scene_step"] = "disabled_start"
            log_event("CHOICE_MADE", "Selected=DisabledShip")
            disabled_ship_scene(state)
    
    else:
        print("  You leave the bridge and head down the main corridor.")

        state["location"] = "corridor"
        state["scene_step"] = "corridor_apple"

        corridor_scene(state)
        
# --------------------------------------
#  Corridor Scene

@safe_action
def corridor_scene(state: dict) -> None:
    state["location"] = "corridor"

    if state.get("scene_step") in ("corridor", "corridor_apple"):
        state["scene_step"] = "corridor_apple"
        save_game(state)

        print("\n  Corridor: you notice an apple sitting on a crate.")

        if not state["flags"].get("corridor_apple_taken"):
            if get_input("  Pick it up? (y/n): ", ["y", "n"]) == "y":
                add_item(state, "Apple")
                state["flags"]["corridor_apple_taken"] = True

        else:
            print("  The crate is empty where the apple used to be.")

        state["scene_step"] = "corridor_coin"
        save_game(state)

    if state.get("scene_step") == "corridor_coin":
        print("\n  A coin glints near a ventilation grate.")

        if not state["flags"].get("corridor_coin_taken"):
            if get_input("  Pick it up? (y/n): ", ["y", "n"]) == "y":
                add_item(state, "Coin")
                state["flags"]["corridor_coin_taken"] = True

        else:
            print("  The coin is gone; you already picked it up.")

        state["scene_step"] = "corridor_encounter"

    if state.get("scene_step") == "corridor_encounter":
        if not state["flags"].get("corridor_encounter_done"):
            corridor_encounter(state)
            state["flags"]["corridor_encounter_done"] = True

        state["scene_step"] = "corridor_junction"
        save_game(state)

    if state.get("scene_step") == "corridor_junction":
        print("\n  You reach a junction with a map terminal.")

        action = get_input(
            "  Open the map, check inventory, or go back to the bridge? (map/inv/back): ",
            ["map", "inv", "back"]
        )

        if action == "map":
            print("  Map: There is The Neutral Zone to the stern")
            save_game(state)

        elif action == "inv":
            show_inventory(state)
            save_game(state)

        else:
            state["location"] = "bridge"
            state["scene_step"] = "bridge_choice"
            start_bridge(state)

# --------------------------------------
#  Colony Ship

@safe_action
def colony_ship_scene(state: dict) -> None:
    state["location"] = "colony_ship"

    if state.get("scene_step") in ("colony_ship", "colony_start"):
        state["scene_step"] = "colony_communicate"
        save_game(state)

        print("""
  You come across a massive generational ship — clearly aged and in disrepair,
  with extremely low energy readings. It's been out here a long, long time.""")

    if state.get("scene_step") == "colony_communicate":
        while True:
            action = get_input(
                "\n  Attempt to communicate or teleport aboard? (c/t): ",
                ["c", "t"]
            )

            if action == "t":
                break

            if "Schematic" not in state["inventory"]:
                if random.random() < 0.5:
                    print(
                        "  A deep scan cuts through the interference — you receive a "
                        "full schematic of the ship."
                    )
                    add_item(state, "Schematic")

                else:
                    print("  You receive no response.")

            else:
                print("  You receive no response.")

        state["scene_step"] = "colony_inside"
        save_game(state)

    if state.get("scene_step") == "colony_inside":
        print("""
  You materialise inside a massive habitat-like structure — an Earth-like
        atmosphere, a simulated day-night cycle. It's breathtaking.""")

        state["scene_step"] = "colony_scan"

    if state.get("scene_step") == "colony_scan":
        while True:
            action = get_input(
                "\n  Look around or scan for life forms? (look/scan): ",
                ["look", "scan"]
            )

            if action == "scan":
                break

            print("  You explore but find nothing immediately useful.")

        print("  Thousands of humanoid life forms detected. There is a house nearby.")

        state["scene_step"] = "colony_find_haru"
        save_game(state)

    if state.get("scene_step") == "colony_find_haru":
        approach = get_input(
            "\n  Search for inhabitants or look for the ship's engineer? (search/engineer): ",
            ["search", "engineer"]
        )

        if approach == "engineer":
            talk_to_npc(state, "haru", add_item, remove_item, get_input, log_event)

        else:
            print("  You find a house — someone answers the door. It's an engineer named Haru.")
            talk_to_npc(state, "haru", add_item, remove_item, get_input, log_event)

        print(
            "\n  You discover these people have no idea they are in space — or that "
            "their ship is failing."
        )

        state["scene_step"] = "colony_repair"

    if state.get("scene_step") == "colony_repair":
        if "Schematic" in state["inventory"]:
            print(
                "\n  You show Haru the schematic. The truth settles over the colony "
                "like a cold wave — they are in space, and their ship is dying."
            )

            print(
                "  Back on the Smenterprise the replicator is on the fritz. "
                "You attempt to fabricate parts."
            )

            choice = get_input(
                "\n  Attempt repairs yourself or teach them to do it? (self/teach): ",
                ["self", "teach"]
            )

            if choice == "self":
                chance = 0.9 if "Coin" in state["inventory"] else 0.7

                if random.random() < chance:
                    print(
                        "\n  Every component fabricated. The colony ship is restored to "
                        "factory condition in record time. The colonists are grateful.\n\n"
                        "  ★  VICTORY — Colony Saved  ★"
                    )
                    log_event("ENDING", "ColonyRepair", "SUCCESS")
                    state["flags"]["ending"] = "ColonyRepair"

                else:
                    print(
                        "\n  The replicator failed on one critical part. You scavenged "
                        "both ships and got things to mostly working order.\n\n"
                        "  ★  VICTORY — Colony Partially Repaired  ★"
                    )
                    log_event("ENDING", "ColonyRepairPartial", "SUCCESS")
                    state["flags"]["ending"] = "ColonyRepairPartial"

            else:
                print(
                    "\n  You walk Haru through every system. The colonists take over "
                    "repairs and succeed — on their own terms.\n\n"
                    "  ★  VICTORY — Colony Self-Sufficient  ★"
                )
                log_event("ENDING", "ColonyTaught", "SUCCESS")
                state["flags"]["ending"] = "ColonyTaught"

        else:
            print(
                "\n  Without a schematic you can't complete repairs. You head back to "
                "search for more resources."
            )
            log_event("CHOICE_MADE", "Colony_NoSchematic")

            state["location"] = "bridge"
            state["scene_step"] = "bridge_choice"
            save_game(state)
            return

    save_game(state)
    delete_save()
    reset_state(state)

    print("\n  [Save data cleared. Thanks for playing!]")

# --------------------------------------
#  Disabled Ship

@safe_action
def disabled_ship_scene(state: dict) -> None:
    state["location"] = "disabled_ship"

    if state.get("scene_step") in ("disabled_ship", "disabled_start"):
        state["scene_step"] = "disabled_mira"

        print(
            "\n  You board the disabled ship. The warp core breach pulses on your "
            "sensors like a countdown."
        )

    if state.get("scene_step") == "disabled_mira":
        talk_to_npc(state, "mira", add_item, remove_item, get_input, log_event)

        state["scene_step"] = "disabled_terminal"
        save_game(state)

    if state.get("scene_step") == "disabled_terminal":
        if "AccessCode" in state["inventory"]:
            print("\n  Mira's access code fragment helps with the terminal.")
            success = terminal_puzzle(state)

        else:
            print("\n  Without an access code the terminal is at full difficulty.")
            success = terminal_puzzle(state)

        if success:
            print(
                "\n  You stabilise the core and escape through the security checkpoint.\n\n"
                "  ★  VICTORY — Core Stabilized  ★"
            )
            log_event("ENDING", "CoreStabilized", "SUCCESS")
            state["flags"]["ending"] = "CoreStabilized"

        else:
            print(
                "\n  You failed to stabilise the core. You escape through maintenance tunnels.\n\n"
                "  ★  ENDING — Maintenance Escape  ★"
            )
            log_event("ENDING", "MaintenanceEscape", "SUCCESS")
            state["flags"]["ending"] = "MaintenanceEscape"

    save_game(state)
    delete_save()
    reset_state(state)

    print("\n  [Save data cleared. Thanks for playing!]")
