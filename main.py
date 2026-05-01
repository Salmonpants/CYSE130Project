import random
#create inventory
inventory = []

#print a starting plot
print("Star date 74219.6\nThe stars hang silent beyond the viewport of the USS Smenterprise, their" \
"light stretched thin across the cold expanse of the Neutral Zone. For nearly a century, the Federation" \
"and the Klingons Star Empire have maintained an uneasy stillness here neither war, nor peace only " \
"distance.")
print("Until now.")
print("A distortion tears through subspace like a wound reopening. Sensors aboard the" \
"Smenterprise shudder as a signal cuts through the static fragmented, repeating, urgent.")
print("This is.. unidentified vessel... repeating distress - drifting... we are not... please" \
"respond - location unstable... hull integrity failing. End transmission.")

#consult with smock
consult_smock = str(input("Would you like to consult with Smock? (y/n): "))
if consult_smock == "y":
    print("Smock: It is smarfleets policy to render aid to anyone in need.")

#enter or do not enter neutral zone
enter_neutral_zone = str(input("Do you want to enter the Neutral Zone? (y/n): "))
if enter_neutral_zone == "y":
    print("You gained an apple")
    inventory.append("Apple")
    
    take_coin = str(input("Walking down the hallway you see a coin. Do you want to pick it up? (y/n)"))
    if take_coin == "y":
        inventory.append("Coin")
    
    print("You have entered the Neutral Zone")
    print("There appears to be 2 ships asking for help. The first one is a colony ship." \
    "The second one appears to be disabled and adrift with a warp core breach getting worse by the second")

    select_ship = str(input("Would you like to enter the colony ship or the disabled ship? (c/d): "))
    if select_ship == "c":
        print("You come across a massive generational ship which looks like it has been in space for a" \
        "considerable amount of time. It seems as though it is in disrepair with extremely low energy readings.")

        communicate_or_teleport = str(input("Would you like to attempt to communicate or teleport aboard? (c/t): "))
        while communicate_or_teleport != "t":
            
                luck = random.randrange(2)

                if inventory.count("Schematic") == 0:
                    if luck == 1:
                        print("A scan provides a schematic of the ship")
                        inventory.append("Schematic")
                else:
                    print("You receive no response")
                
                communicate_or_teleport = str(input("Would you like to attempt to communicate or teleport aboard? (c/t)"))
        
        print("You are greeted with a massive habitat like structure with an earth-like atmosphere and" \
        "a day night cycle.")

        look_or_scan = str(input("Would you like to look around or scan for life forms? (l/s): "))
        while look_or_scan != "s":
            print("Thousands of humanoid lifeforms are detected")
            look_or_scan = str(input("Would you like to look around or scan for life forms? (l/s): "))
        
        print("There is a house nearby")
        knock_or_ring = str(input("Would you like to knock on the door or ring the bell? (k/r): "))
        print("Someone comes to the door and asks you what you need. He provides information and help." \
        "You find out that these people do not realize that they are in space and that their ship is failing.")

        print("Would you like to try to repair the ship without the denizens or educate them on how to repair" \
        "it themselves? (r/e): ")
        if (inventory.count("Schematic") == 1):
            print("You show them the ship schematic. They realize they are on a failing ship. Going back" \
            "to the Smenterprise you find that your replicator is on the frits and intermittently making" \
            "things. You attempt to make parts for the ship.")
            if (inventory.count("Coin") == 1):
                if (random.randrange(0, 10) > 1):
                    print("You successfully made the ship components. You greatly repair the ship to factory or" \
                    "better conditions and complete the great repairs in record time. The people are greatful" \
                    "and continue on their newly repaired mission. Victory")
                else:
                    print("The replicator was failed to produce a part and was damaged. You and the crew" \
                    "proceed to scavange around their ship and get things to mostly working order. Victory.")
            else:
                if (random.randrange(0, 10) > 3):
                    print("You successfully made the ship components. You greatly repair the ship to factory or" \
                    "better conditions and complete the great repairs in record time. The people are greatful" \
                    "and continue on their newly repaired mission. Victory")
                else:
                    print("The replicator was failed to produce a part and was damaged. You and the crew" \
                    "proceed to scavange around their ship and get things to mostly working order. Victory.")
        else:
            pass

    elif select_ship == "d":
        pass

elif enter_neutral_zone == "n":
    print("Game over: The phage overtakes another Vidiian colony")

else:
    print("error")

#general loop
#print situation
#get input for decision
#branch/consequence

#use some randomness