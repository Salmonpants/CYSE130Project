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
    pass

#general loop
#print situation
#get input for decision
#branch/consequence

#use some randomness