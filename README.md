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

**Main story paths**

1. **Colony Ship Path** — investigate the colony ship and attempt repairs.  
2. **Disabled Ship Path** — board the disabled ship and attempt core stabilization.  
3. **Bridge and Corridor Path** — explore the Smenterprise, collect items, and influence other paths.

**Example endings**

- **ColonyRepair** — colony saved (victory).  
- **biscut_trade** — peaceful resolution by trading the pet.  
- **captured** — captured during combat (bad ending).  

> Update this list with the exact ending keys found in `scenes.py` before final submission.

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
- **Drone encounter** — corridor combat; success lets you pass, failure injures you or forces retreat.

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

