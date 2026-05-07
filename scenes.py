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

        sel = get_input("  Which do you approach? (c/d): ", ["c", "d"])

        if sel == "c":
            state["location"] = "colony_ship"
            state["scene_step"] = "colony_start"
            log_event("CHOICE_MADE", "Selected=ColonyShip")
            colony_ship_scene(state)

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
            print("  Map: colony ship to port — disabled ship to starboard.")
            save_game(state)

        elif action == "inv":
            show_inventory(state)
            save_game(state)

        else:
            state["location"] = "bridge"
            state["scene_step"] = "bridge_choice"
            start_bridge(state)


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
<<<<<<< HEAD
                    )
                    add_item(state, "Schematic")

                else:
                    print("  You receive no response.")
=======
                    )
                    add_item(state, "Schematic")

                else:
                    print("  You receive no response.")
>>>>>>> parent of c7e75e0 (Pre error check Finished greater story correction)

            else:
                print("  You receive no response.")

        state["scene_step"] = "colony_inside"
        save_game(state)

    if state.get("scene_step") == "colony_inside":
        print("""
  You materialise inside a massive habitat-like structure — an Earth-like
<<<<<<< HEAD
        atmosphere, a simulated day-night cycle. It's breathtaking.""")

        state["scene_step"] = "colony_scan"

    if state.get("scene_step") == "colony_scan":
=======
        atmosphere, a simulated day-night cycle. It's breathtaking.""")

        state["scene_step"] = "colony_scan"

    if state.get("scene_step") == "colony_scan":
>>>>>>> parent of c7e75e0 (Pre error check Finished greater story correction)
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
<<<<<<< HEAD
=======
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
#  Disabled Ship Arrival
def disabled_ship_arrival_scene(state):
    state["location"] = "outside_ship"
    print(
            "\n  You drop out of warp and infront of you is the disabled ship. "
            "The ship is a D7-class battlecruiser in the middle of nowhere"
            "The sensors show there is 223 crewmembers left on board and the core is about to breach"
            "(d) Drop shields and attempt to teleport the survivors off of the ship"
            "(t) Teleport aboard and try to stabalize the ship"
>>>>>>> parent of c7e75e0 (Pre error check Finished greater story correction)
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
<<<<<<< HEAD
            log_event("ENDING", "MaintenanceEscape", "SUCCESS")
            state["flags"]["ending"] = "MaintenanceEscape"
=======
        
        if "biscut" not in state["inventory"]:
            sel = get_input("  Emergency beamout (e): ", ["e"])
            print("You realize there is no negotiating with Smlaa so you enact emergency beam out")
            state["scene_step"] = "combat_start"
            state["location"] = "smenterprise_bridge"
            disabled_ship_combat_scene(state)
        else:
            print("(e) Emergency beam out to the Smenterprise and keep biscut as a pet"
                  "(g) Give Smlaa Biscut as a gift it may help the current situation")
            sel = get_input("  Which do you approach? (e/g): ", ["e", "g"])
            if(sel == "t"):
                state["scene_step"] = "combat_start"
                state["location"] = "smenterprise_bridge"
                disabled_ship_combat_scene(state)
            else:
                print(
                    "After you gave Smlaa biscut you realize that is what he was so distraught about losing"
                    "Smlaa says these ships are so large there are so many places for a targ to hide"
                    "He is just so full of joy that he lets you and your crew go unscathed with a heartfelt appology"
                    "You and your crew head back to starbase 10 happy to be alive")
                log_event("ENDING", "biscut_trade", "SUCCESS")
                state["flags"]["ending"] = "biscut_trade"
                delete_save()
                reset_state(state)
                print("\n  [Save data cleared. Thanks for playing!]")     
            
            
            
def disabled_ship_combat_scene(state):
    if state.get("scene_step") == "combat_start":
        print(
            "You got out of there just in time to not be gutted like a fish"
            "Now there are more problems you are looking down the barrels of multiple fully armed "
            "Birds-of-Prey.  You are we are heavily outgunned captain a bridge officer says\n")
        if "Apple" in state["inventory"]:
            print("(r) Try to warp out and escape"
                  "(t) Talk to engineering "
                  "(a) Use apple")
            sel = get_input("  Which do you choose? (r/t/a): ", ["r", "t","a"])
            if sel == "r":
                print("They are jamming warp travel")
                state["scene_step"] = "combat_middle"
            elif sel == "t":
                    talk_to_npc(state, "Smotty", add_item, remove_item, get_input, log_event)
                    disabled_ship_combat_scene(state)
            else:
                print("using the apple made the Smenterprises bridge sutdown and reeboot"
                      "The tactical officer informs you that all of the enemy shields are down"
                      "One photon each should do lets not waste ammunition")
                talk_to_npc(state, "Smones", add_item, remove_item, get_input, log_event)
                print("Having foiled the smlingons attempt at an ambush against insurmountable odds"
                      "you end the day victorious as you repair and set a course for starbase 10")
                log_event("ENDING", "an_apple_a_day", "SUCCESS")
                state["flags"]["ending"] = "an_apple_a_day"
                delete_save()
                reset_state(state)
                print("\n  [Save data cleared. Thanks for playing!]")           
        else:
            print("(r) Try to warp out and escape"
                  "(t) Talk to engineering")
            sel = get_input("  Which do you choose? (r/t): ", ["r", "t"])
            if sel == "r":
                print("They are jamming warp travel")
                state["scene_step"] = "combat_middle"
            else:
                    talk_to_npc(state, "Smotty", add_item, remove_item, get_input, log_event)
                    disabled_ship_combat_scene(state)
                    
    if state.get("scene_step") == "combat_middle":  
        survival = random.randint(1,10)
        if "Coin" in state["inventory"]:
            if(survival > 4):
                state["scene_step"] = "victory"
            else:
                state["scene_step"] = "captured"
        else:
            if(survival < 5):
                state["scene_step"] = "victory"
            else:
                state["scene_step"] = "captured"
                
    if state.get("scene_step") == "victory":
        print("Though fiber defficient, battered, and deminished in the eyes of defete the Smenterprise and her crew endured."
              "Against overwhelming odds, they seized the moment and thwarted the Smlingons carefully laid ambush, turning near"
              "disaster into hard-won victory.")
        log_event("ENDING", "hard_won", "SUCCESS")
        state["flags"]["ending"] = "hard_won"
        delete_save()
        reset_state(state)
        print("\n  [Save data cleared. Thanks for playing!]")      
    else:
        print("Though, in the eyes of defeat, the Smenterprise and her crew had fought hard with unwavering resolve,"
              "their efforts were not enough.  Surrounded and outmatched, they were untimately captured-yet even in chains, their"
              "defiance endured")
        log_event("ENDING", "captured", "SUCCESS")
        state["flags"]["ending"] = "captured"
        delete_save()
        reset_state(state)
        print("\n  [Save data cleared. Thanks for playing!]") 
        #save_game(state)
        #delete_save()
        #reset_state(state)
>>>>>>> parent of c7e75e0 (Pre error check Finished greater story correction)

    save_game(state)
    delete_save()
    reset_state(state)

    print("\n  [Save data cleared. Thanks for playing!]")
