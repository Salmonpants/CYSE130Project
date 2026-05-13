# USS SMENTERPRISE — Text Adventure

# Team:
  # Ali F A A Abbas
  # Amy Fernandez Garcia 
  # Brian Honadle  
  # Evan Kujawa 
  # Jad Labriny 
  # Hudson Neely 
  
# Repository:  _ GitHub repo link here_

## Overview

A Python terminal text‑adventure with branching storylines, NPC interactions, an inventory system, puzzles and combat, and the required **Cyber Pack** (input validation, audit logging, save/load tamper detection). The game saves progress to a JSON save file and writes an audit log for security‑relevant events.

## Quick start

**Requirements**

- **Python 3.9+** (3.10 recommended)  
- No external packages required (standard library only)

**Files of interest**

- `main.py` — game launcher and main menu  
- `scenes.py` — story scenes and branching logic  
- `minigames.py` — puzzles and encounters  
- `npcs.py` — NPC interactions  
- `inventory.py` — inventory functions  
- `save_system.py` — save/load with tamper detection  
- `logger.py` — audit logging (writes `audit_log.txt`)  
- `errors.py`, `input_helpers.py`, `state.py` — core engine helpers

## Core features

- **Branching story** with multiple endings and meaningful choices  
- **5+ locations** and major events (bridge, corridor, colony ship, disabled ship, combat)  
- **5+ NPCs** with dialogue, trades, and rewards  
- **Inventory system** (collect, view, use items)  
- **2+ challenges** (terminal puzzle, drone encounter/combat)  
- **Cyber Pack**: input validation, audit logging, save/load tamper detection

## Story paths and endings

### Main story paths

1. **Colony Ship Path**  
   Investigate an ancient generational colony ship drifting through space.  
   Choices involving diplomacy, schematics, repairs, and cooperation determine the outcome.

2. **Disabled Ship Path**  
   Board a disabled Klingon D7-class battlecruiser and attempt to stabilize its warp core.  
   Includes terminal puzzles, exploration, combat, and moral decisions.

3. **Bridge and Corridor Path**  
   Explore the USS Smenterprise, collect important items like the Apple and Coin, unlock access routes, and influence later story outcomes.

---

## All Story Endings

### Neutral / Early Ending

- **Ignored calls for help**  
  The player ignores both distress calls and returns home, only to face consequences from Smarfleet for abandoning those in need.

---

### Colony Ship Endings

- **ColonyRepair** — *Best Ending*  
  The colony ship is fully repaired and restored to factory condition.

- **Lost_Supplies**  
  The replicated repair parts are lost, but the colony ship is repaired enough to survive.

- **ColonyRepairPartial**  
  The replicator fails to create a critical part, forcing partial repairs.

- **ColonyRepairGroup** — *Group Success Ending*  
  The colonists fully understand their situation and work together with your crew to completely restore the ship.

- **ColonyRepairGroupSuppliesLost**  
  The colony ship survives thanks to teamwork, despite losing vital supplies.

- **ColonyPartialGroup**  
  The replicator fails, but the combined efforts of both crews repair the ship enough to continue its journey.

---

### Disabled Ship Endings

- **unable to help**  
  Failure to stabilize the warp core results in massive casualties and retreat.

- **biscut_trade** — *Peaceful Ending*  
  Returning Biscut the targ to Captain Smlaa peacefully resolves the conflict.

---

### Combat Endings

- **an_apple_a_day** — *Secret / Joke Victory Ending*  
  Using the Apple causes a systems reboot that disables enemy shields, allowing the Smenterprise to defeat overwhelming odds.

- **hard_won**  
  The Smenterprise survives an ambush and wins a desperate battle against multiple Birds-of-Prey.

- **captured** — *Bad Ending*  
  The crew fights bravely but is ultimately overwhelmed and captured.

---

## Choice and Item Impact

Several inventory items directly influence endings and gameplay outcomes:

- **Apple** — unlocks a hidden combat victory route.
- **Coin** — improves odds during critical random events.
- **Ship_Schematic** — enables better colony ship repair outcomes.
- **biscut** — unlocks the peaceful resolution ending.
- **AccessCode** — assists with terminal puzzles aboard the disabled ship.
```

## Locations and major events

- **Bridge** — start location, talk to Smock, choose mission.  
- **Corridor** — find Apple and Coin; map terminal.  
- **Colony Ship** — scan, teleport aboard, replicate parts, multiple outcomes.  
- **Disabled Ship** — terminal puzzles, puppy room, core stabilization.  
- **Combat** — final combat encounter and escape/capture outcomes.

## NPCs

- **Smock (Bridge)** — gives **HintToken** and sets helpful flags.  
- **Haru (Colony Ship)** — provides clues about schematics.  
- **Mira (Disabled Ship)** — trades **Coin** for **AccessCode** fragment.  
- **Guard** — blocks passage; dialogue affects access.  
- **Trader** — trades **Coin** for **MedPatch**.

Include in README where each NPC appears and what they do (clue, trade, item, or trigger).

## Inventory items

- **Apple** — distraction or special outcome trigger.  
- **Coin** — used for trades (AccessCode, MedPatch).  
- **AccessCode** — lowers difficulty of terminal puzzles.  
- **Ship_Schematic** — used to repair the colony ship.  
- **Ship_Components** — influences colony repair ending.

## Challenges

- **Terminal puzzle** — occurs on the disabled ship terminal; success disables alarms, failure may trigger a sweep or other consequences.  
- **Locked corridor** — guess the number to open the door; success lets you pass, failure causes the number to change.

## Cyber Pack

1. **Input validation and safe error handling**  
   - All user input is validated via `input_helpers.py`.  
   - `errors.safe_action` centralizes `KeyboardInterrupt` and game errors to avoid crashes.

2. **Audit logging**  
   - Security‑relevant events are appended to `audit_log.txt` via `logger.log_event`.  
   - Typical events: `GAME_START`, `SAVE_ATTEMPT`, `LOAD_ATTEMPT`, `CHALLENGE_ATTEMPT`, `ITEM_ACQUIRED`, `ENDING`.

3. **Save and load with tamper detection**  
   - Saves include an integrity check (SHA‑256). The loader verifies the hash and rejects tampered saves.  
   - If your implementation stores the hash inside the same file, consider switching to a separate `.hash` file or an HMAC for stronger protection.

