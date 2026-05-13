import random
import time
from errors import safe_action
from input_helpers import get_input
from inventory import add_item, remove_item, show_inventory
from save_system import save_game, delete_save
from logger import log_event
from npcs import talk_to_npc
from minigames import terminal_puzzle, corridor_encounter, corridor_access_puzzle
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
        "\n  Talk to Smock, check the console, or leave the bridge? (talk/console/leave): ",
        ["talk", "console", "leave"]
    )

    if choice == "talk":
        talk_to_npc(state, "smock", add_item, remove_item, get_input, log_event)
        print()
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
            
        elif sel == "i":
            print("\nIn the light of political unrest you decided to leave and ignore those calls")
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
            disabled_ship_arrival_scene(state)
    
    else:
        if not state["flags"].get("corridor_access_granted"):
            if not corridor_access_puzzle(state):
                print("  Access denied. You remain on the bridge.")
                state["location"] = "bridge"
                state["scene_step"] = "bridge_choice"
                save_game(state)
                return

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

        state["scene_step"] = "corridor_junction"

    if state.get("scene_step") == "corridor_junction":
        print("\n  You reach a junction with a map terminal.")

        action = get_input(
            "\n  Open the map, check inventory, or go back to the bridge? (map/inv/back): ",
            ["map", "inv", "back"]
        )

        if action == "map":
            print("\n  Map: There is The Neutral Zone to the bow")
            corridor_scene(state)
            save_game(state)

        elif action == "inv":
            show_inventory(state)
            corridor_scene(state)
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
        print("(c) Attempt to Communicate")
        print("(t) Attempt to teleport aboard")
        print("(s) Attempt to scan the ship")
        action = get_input("\n  Which do you do? (c/t/s): ",["c", "t","s"])

        if action == "t":
            state["scene_step"] = "borded_colony"
            save_game(state)
            
        elif(action == 'c'):
            print("\n  You attempt to communicate but the only response is the silence of space")
            state["scene_step"] = "colony_communicate"
            colony_ship_scene(state)
            save_game(state)
        else:
            if not state["flags"].get("ship_schematic_taken"):
                print("After tedious amounts of multi phasic, gamma, neutrino, thermal, and structural scans you gain a full schematic of the ship")
                if get_input("  Pick it up? (y/n): ", ["y", "n"]) == "y":
                    add_item(state, "Ship_Schematic")
                    state["flags"]["ship_schematic_taken"] = True
                    save_game(state)

            else:
                print("There is nothing else to learn from this ship")
            save_game(state)    
        
        
    if state.get("scene_step") == "borded_colony":    
        print(
            """\n  You materialise inside a massive habitat-like structure — an Earth-like
        atmosphere, a simulated day-night cycle. It's breathtaking.\n"""
        )
        print("    (s) Scan the surroundings")
        print("    (l) Look around")
        
        while(True):
            sel = get_input("  Which do you approach? (s/l): ", ["s", "l"])
            if(sel == "s"):
                print("  Thousands of humanoid life forms detected. There is a house nearby\n")
            else:
                break
        print("\n  There is a nice looking house nearby")
        print("    (r) Ring the door bell")
        print("    (k) Knock")
        sel = get_input("  Which do you approach? (r/k): ", ["r", "k"])
        state["scene_step"] = "colony_house"
        save_game(state)
    
    if state.get("scene_step") == "colony_house":
        print()  
        talk_to_npc(state, "haru", add_item, remove_item, get_input, log_event)
        
        print("\n  You discover these people have no idea they are in space and that their ship is failing\n")
        
        print("    (t) Try to affect repairs yourself and leave the denizens to not know")
        print("    (e) Educate them on their current situation and have them help with the repairs\n")
        
        sel = get_input("  Which do you approach? (t/e): ", ["t", "e"])
        print()
        
        if sel == "t":
            state["scene_step"] = "colony_ship_solo"
            save_game(state)
        else:
            state["scene_step"] = "colony_ship_together"
    
    if state.get("scene_step") == "colony_ship_solo":
        
        print("Arriving back after your exploration you find that your replicatior is on the fritz"
              "and intermitantly making things and you attempt to make parts for the colony ship.")
         
        if "Coin" in state["inventory"]:
            val = random.randint(1,10)
            if val > 1:
                state["scene_step"] = "colony_ship_replicator_success1"
            else:
                state["scene_step"] = "colony_ship_replicator_failure1"
            
        else:
            val = random.randint(1,10)
            if val > 3:
                state["scene_step"] = "colony_ship_replicator_success1"
            else:
                state["scene_step"] = "colony_ship_replicator_failure1"
                
    if state.get("scene_step") == "colony_ship_replicator_success1":
        if not state["flags"].get("ship_components_taken"):
                    if get_input("  Take them with you? (y/n): ", ["y", "n"]) == "y":
                        add_item(state, "Ship_Components")
                        state["flags"]["ship_components_taken"] = True
                        save_game(state)
        if "Ship_Components" in state["inventory"]:
             
            print(
                "\n  Every component fabricated. The colony ship is restored to "
                "factory condition in record time. The colonists are grateful.\n\n"
                "  ★  VICTORY — Colony Saved  ★"
                            )
            log_event("ENDING", "ColonyRepair", "SUCCESS")
            state["flags"]["ending"] = "ColonyRepair"
        else:
            print(
               "The parts that were just maid got lost and the replicator is completely broken"
               "The crew did the best they can and got it back up to half of new, but that is good enough we hope"
                            )
            log_event("ENDING", "Lost_Supplies", "SUCCESS")
            state["flags"]["ending"] = "Lost_Supplies"
        save_game(state)
        delete_save()
        reset_state(state)
        print("\n  [Save data cleared. Thanks for playing!]")

        
    if state.get("scene_step") == "colony_ship_replicator_failure1":
        print(
            "\n  The replicator failed on one critical part. You scavenged "
            "both ships and got things to mostly working order.\n\n"
            "  ★  Good Job — Colony Partially Repaired  ★"
                    )
                    
        log_event("ENDING", "ColonyRepairPartial", "SUCCESS")
        state["flags"]["ending"] = "ColonyRepairPartial"
        save_game(state)
        delete_save()
        reset_state(state)
        print("\n  [Save data cleared. Thanks for playing!]")
                       
            
    if state.get("scene_step") == "colony_ship_together":
        
        
        if "Ship_Schematic" in state["inventory"]:
            
            print("    (u) Use the ship schematic")
            print("    (e) Educate them and try to get them to fully understand their position")
            sel = get_input("  Which do you approach? (u/e): ", ["u", "e"])
            if(sel == "u"):
                print("\n  Using the ship schematic proves effective")
                state["scene_step"] = "colony_ship_understanding_success"
            else:
                state["scene_step"] = "colony_ship_understanding"
        else:
            state["scene_step"] = "colony_ship_understanding"
        
    if state.get("scene_step") == "colony_ship_understanding":
        val = random.randint(1,10)
        if "Coin" in state["inventory"]:
            if val > 3:
                state["scene_step"] = "colony_ship_understanding_success"
            else:
                state["scene_step"] = "colony_ship_understanding_failure"
            
        else:
            if val > 5:
                state["scene_step"] = "colony_ship_understanding_success"
            else:
                state["scene_step"] = "colony_ship_understanding_failure"
                
    if state.get("scene_step") == "colony_ship_understanding_success":
        print("\n  You took the the time to educate them about the entire scope of their problems. "
              "They were rightfuly not believeing this story, but with effort you won them over. "
              "The crew of the colony ship is ready to help you help them. ")
        state["scene_step"] = "colony_ship_group"
    
    if state.get("scene_step") == "colony_ship_understanding_failure":
        print("Unfortunatly no matter what was said it seems as they will never believe you or your story. "
              "But smarfleet is in th buisness of helping those in need even if they don't know it. ")
        state["scene_step"] = "colony_ship_solo"
        colony_ship_scene(state)
    
    if state.get("scene_step") == "colony_ship_group":
        
        print("Arriving back after your exploration you find that your replicatior is on the fritz"
              "and intermitantly making things and you attempt to make parts for the colony ship")
        val = random.randint(1,10)
        
        if "Coin" in state["inventory"]:
            if val > 1:
                state["scene_step"] = "colony_ship_replicator_success2"
            else:
                state["scene_step"] = "colony_ship_replicator_failure2"
            
        else:
            if val > 3:
                state["scene_step"] = "colony_ship_replicator_success2"
            else:
                state["scene_step"] = "colony_ship_replicator_failure2"
                
    if state.get("scene_step") == "colony_ship_replicator_success2":
        if not state["flags"].get("ship_components_taken"):
                    if get_input("  Take them with you? (y/n): ", ["y", "n"]) == "y":
                        add_item(state, "Ship_Components")
                        state["flags"]["ship_components_taken"] = True
                        save_game(state)
        
        if "Ship_Components" in state["inventory"]:
             
            print(
                "You greatly repair the ship to factory or better conditions and complete the extrenuous repairs in record time. "
                "The people are greateful for the help and now have an understading of where their lives are going with a renewed mission"
                            )
            log_event("ENDING", "ColonyRepairGroup", "SUCCESS")
            state["flags"]["ending"] = "ColonyRepairGroup"
            save_game(state)
            delete_save()
            reset_state(state)
            print("\n  [Save data cleared. Thanks for playing!]")
        else:
            print(
               "The parts that were just made got lost and the replicator is completely broken. "
               "The crew did the best they can and got it back up to half of new, but that is good enough we hope."
                            )
            log_event("ENDING", "ColonyRepairGroupSuppliesLost", "SUCCESS")
            state["flags"]["ending"] = "ColonyRepairGroupSuppliesLost"
            save_game(state)
            delete_save()
            reset_state(state)
            print("\n  [Save data cleared. Thanks for playing!]")
    if state.get("scene_step") == "colony_ship_replicator_failure2":
        print(
            "The crew is dissapointed that the replicator failed, but with their new found understanding they were able to work with you and your crew"
            "to not repair the ship all the way but enough to get them where they were going"
                        )
        log_event("ENDING", "ColonyPartialGroup", "SUCCESS")
        state["flags"]["ending"] = "ColonyPartialGroup"
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
            "The ship is a D7-class battlecruiser in the middle of nowhere. "
            "The sensors show there is 223 crewmembers left on board and the core is about to breach."
        )
    print("  (d) Drop shields and attempt to teleport the survivors off of the ship")
    print("  (t) Teleport aboard and try to stabalize the ship")
    sel = get_input("  Which do you approach? (d/t): ", ["d", "t"])
    if(sel == "d"):
        state["scene_step"] = "combat_start"
        print("\nHaving to drop your shields in order to teleport the crew off of their ship left you vulnerable to attack.")
        print("You now find out that this was no ship in distress, but a trap.")
        disabled_ship_combat_scene(state)
    else:
        disabled_ship_scene(state)
        
        
# --------------------------------------
#  Disabled Ship Boarding

@safe_action
def disabled_ship_scene(state: dict) -> None:
    state["location"] = "disabled_ship"

    if state.get("scene_step") in ("disabled_ship", "disabled_start"):

        print(
            "\n  You board the disabled ship. The warp core breach pulses on your "
            "sensors like a countdown.  Suddenly you hear wimpering coming from a locked door next to you"
            "\n(t) Talk with Mira"
            "\n(a) Attempt to unlock the door"
            "\n(c) continue on"
        )
        sel = get_input("  Which do you approach? (t/a/c): ", ["t", "a","c"])
        
        if(sel == "t"):
            state["scene_step"] = "disabled_mira"
        elif(sel == "a"):
            state["scene_step"] = "disabled_terminal"
        else:
            state["scene_step"] = "big_decision"
        
        
    if state.get("scene_step") == "disabled_mira":
        print()
        talk_to_npc(state, "mira", add_item, remove_item, get_input, log_event)
        state["scene_step"] = "disabled_start"
        save_game(state)
        disabled_ship_scene(state)
        
        

    if state.get("scene_step") == "disabled_terminal":
        if "AccessCode" in state["inventory"]:
            print("\n  Mira's access code fragment helps with the terminal.")
            success = terminal_puzzle(state)

        else:
            print("\n  Without an access code the terminal is at full difficulty.")
            success = terminal_puzzle(state)

        if success:
            state["scene_step"] = "puppy_room"
            save_game(state)
        else:
            print("You failed to open the door")
            state["scene_step"] = "disabled_ship"
            state["location"] = "disabled_ship"
            disabled_ship_scene(state)
            
        if state.get("scene_step") == "puppy_room":
            state["scene_step"] = "puppy_room"
            save_game(state)

            print(
            "\nYou open the door and find yourself looking at a most peculure creature."
            "It looks like a mixture of wild boar and a bulldog.  It has a low, wide"
            "body with short, thick legs.  Its head is big and round with a flat snout,"
            "a wide mouth, and two sharp tusks sticking out.  The skin is rough and wrinkled,"
            "often dark brown or gray, with little to no hair.  Its eyes are small and deep"
            ", and its ears are short and slightly pointed. It has a name tag biscut\n"
            )

            if not state["flags"].get("puppy_room_taken"):
                if get_input("  Take him with you? (y/n): ", ["y", "n"]) == "y":
                    add_item(state, "biscut")
                    state["flags"]["puppy_room_taken"] = True
                    save_game(state)

        else:
            print("The room is empty.")
        state["scene_step"] = "core_stabilization"
        save_game(state)

        
            
    if state.get("scene_step") == "core_stabilization":
        save_game(state)
        print(
                "\nYou finally get to the core room everything is red alarms are blaring there is steam everywhere. "
                "Your engineer thinks it can be a quick fix, but it seems the console is locked. "
                "It apears to be the same type of lock at the other door."
            )
        success = False
        success = terminal_puzzle(state)
        if(success):
            print(
                "The console has been unlocked and the core has now been stabalized"
                "While you were waiting for the engineer to work their magic you discover an ambush plot"
                "Unfortunatly while you were reading one of the survivors saw what you were reading and they cant let that info leave"
                "Your crew is taken before the captain of the ship"
                )
            state["scene_step"] = "taken_to_captain"
            save_game(state)
        else:
            print(
                "\nYou were unable to access the panel and the smlingon ship is about to blow."
                "Emergency transport is activated unfortunatly you and some of your crew made it back."
                "the rest of your crew and the smlinons were blown up."
                "You take whats left of your crew back to starbase 10."
                )
            log_event("ENDING", "unable to help", "SUCCESS")
            state["flags"]["ending"] = "unable to help"
            delete_save()
            reset_state(state)
            print("\n  [Save data cleared. Thanks for playing!]")   
             
    if state.get("scene_step") == "taken_to_captain":
        
        print("Hello smarfleet my name is Smlaa, the captain of this fine vessle. Due to the loss of my favorite thing "
              "I have little to no patence for insolence.  I hear that you have gotten your hands on some information "
              "that should have been left alone.  I plan on killing you and your friends based on the information you read."
              "You know I can as there is an entire fleet cloaked off your bow.\n"
            )
        
        if "biscut" not in state["inventory"]:
            sel = get_input("  Emergency beam out (e): ", ["e"])
            print("You realize there is no negotiating with Smlaa so you enact emergency beam out")
            state["scene_step"] = "combat_start"
            state["location"] = "smenterprise_bridge"
            save_game(state)
            print("You got out of there just in time to not be gutted like a fish")
            disabled_ship_combat_scene(state)
        else:
            print("(e) Emergency beam out to the Smenterprise and keep biscut as a pet"
                  "(g) Give Smlaa Biscut as a gift it may help the current situation")
            sel = get_input("  Which do you approach? (e/g): ", ["e", "g"])
            if(sel == "e"):
                state["scene_step"] = "combat_start"
                state["location"] = "smenterprise_bridge"
                save_game(state)
                print("You got out of there right before getting skinned alive.")
                disabled_ship_combat_scene(state)
            else:
                print(
                    "After you gave Smlaa biscut you realize that is what he was so distraught about losing. "
                    "Smlaa says these ships are so large there are so many places for a targ to hide. "
                    "He is just so full of joy that he lets you and your crew go unscathed with a heartfelt appology. "
                    "You and your crew head back to starbase 10 happy to be alive.")
                log_event("ENDING", "biscut_trade", "SUCCESS")
                state["flags"]["ending"] = "biscut_trade"
                delete_save()
                reset_state(state)
                print("\n  [Save data cleared. Thanks for playing!]")     
            
# --------------------------------------
#  Disabled Ship Combat Scene           
            
def disabled_ship_combat_scene(state):
    state["location"] = "smenterprise_bridge"
    
    if state.get("scene_step") == "combat_start":
        print(
            "\nNow there are more problems as you are looking down the barrels of multiple fully armed "
            "Birds-of-Prey.  \nWe are heavily outgunned captain a bridge officer says\n")
        if "Apple" in state["inventory"]:
            print("(r) Try to warp out and escape"
                  "\n(t) Talk to engineering "
                  "\n(a) Use apple")
            sel = get_input("  Which do you choose? (r/t/a): ", ["r", "t","a"])
            if sel == "r":
                print("They are jamming warp travel")
                state["scene_step"] = "combat_middle"
                save_game(state)
            elif sel == "t":
                    talk_to_npc(state, "Smotty", add_item, remove_item, get_input, log_event)
                    disabled_ship_combat_scene(state)
            else:
                print("using the apple made the Smenterprises bridge sutdown and reeboot\n"
                      "The tactical officer informs you that all of the enemy shields are down\n"
                      "One photon each should do lets not waste ammunition")
                talk_to_npc(state, "Smones", add_item, remove_item, get_input, log_event)
                print("\nHaving foiled the smlingons attempt at an ambush against insurmountable odds\n"
                      "you end the day victorious as you repair and set a course for starbase 10")
                log_event("ENDING", "an_apple_a_day", "SUCCESS")
                state["flags"]["ending"] = "an_apple_a_day"
                delete_save()
                reset_state(state)
                print("\n  [Save data cleared. Thanks for playing!]")           
        else:
            print("(r) Try to warp out and escape"
                  "\n(t) Talk to engineering")
            sel = get_input("  Which do you choose? (r/t): ", ["r", "t"])
            if sel == "r":
                print("They are jamming warp travel")
                print("There is no option, but to fight now")
                state["scene_step"] = "combat_middle"
                save_game(state)
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
        for i in range(5):
            print("fighting")
            time.sleep(1)
                
    if state.get("scene_step") == "victory":
        print("Though fiber deficient, battered, and diminished in the eyes of defeat the Smenterprise and her crew endured."
              "Against overwhelming odds, they seized the moment and thwarted the Smlingons carefully laid ambush, turning near"
              "disaster into hard-won victory."  )
        log_event("ENDING", "hard_won", "SUCCESS")
        state["flags"]["ending"] = "hard_won"
        delete_save()
        reset_state(state)
        print("\n  [Save data cleared. Thanks for playing!]")      
    if state.get("scene_step") == "captured":
        print("\nThough, in the eyes of defeat, the Smenterprise and her crew had fought hard with unwavering resolve,\n"
              "their efforts were not enough.  Surrounded and outmatched, they were ultimately captured-yet even in chains, their"
              " defiance endured")
        log_event("ENDING", "captured", "SUCCESS")
        state["flags"]["ending"] = "captured"
        delete_save()
        reset_state(state)
        print("\n  [Save data cleared. Thanks for playing!]") 
        
