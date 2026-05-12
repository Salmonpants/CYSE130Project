def talk_to_npc(state, npc_name, add_item, remove_item, get_input, log_event):
    npc_name = npc_name.lower()

    # NPC 1: Smock (Bridge Guide)
    if npc_name == "smock":
        print('Smock: "It is Smarfleet\'s policy to render aid to anyone in need."')
        print('Smock: "Check the terminal and decide which ship needs you most."')

        state["flags"]["talked_to_smock"] = True

    # NPC 2: Haru (Colony Ship Engineer)
    elif npc_name == "haru":
        print('Haru: "Our systems are breaking down faster than we can repair them."')
        print('Haru: "If you find a schematic, we may still be able to save the ship."')

        state["flags"]["talked_to_haru"] = True

    # NPC 3: Mira (Disabled Ship Scientist)
    elif npc_name == "mira":
        print('Mira: "The warp core is unstable. I have part of an access code."')
        print('Mira: "If you can help me, I can help you stabilize the ship."')

        state["flags"]["talked_to_mira"] = True

        if "AccessCode" not in state["inventory"]:
            if "Coin" in state["inventory"]:
                trade = get_input("Trade your Coin for the AccessCode? (y/n): ", ["y", "n"])
                if trade == "y":
                    remove_item(state, "Coin")
                    add_item(state, "AccessCode")
                    log_event("NPC_TRADE", "NPC=Mira Coin->AccessCode", "SUCCESS")
                else:
                    print('Mira: "Come back if you change your mind."')
            else:
                print('Mira: "Bring me a coin and I will give you the code fragment."')

    # NPC 4: Guard
    elif npc_name == "guard":
        print('Guard: "No one passes through here without proof they belong."')
        print('Guard: "If you help restore order, I may let you through."')

        state["flags"]["talked_to_guard"] = True

    # NPC 5: Trader
    elif npc_name == "trader":
        print('Trader: "I trade useful supplies for valuable little objects."')
        print('Trader: "A coin could get you something that keeps you alive."')

        state["flags"]["talked_to_trader"] = True

        if "Coin" in state["inventory"] and "MedPatch" not in state["inventory"]:
            trade = get_input("Trade your Coin for a MedPatch? (y/n): ", ["y", "n"])
            if trade == "y":
                remove_item(state, "Coin")
                add_item(state, "MedPatch")
                log_event("NPC_TRADE", "NPC=Trader Coin->MedPatch", "SUCCESS")
            else:
                print('Trader: "Suit yourself."')
        elif "MedPatch" in state["inventory"]:
            print('Trader: "I already gave you what I had."')
        else:
            print('Trader: "Come back with a coin."')

    elif npc_name == "smotty":
        print('Smotty: "I\'m given her all she\'s got captain"')

    else:
        print("There is no one here by that name.")
