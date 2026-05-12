import random

from errors import safe_action, InputError
from input_helpers import get_input, prompt_menu_number
from inventory import remove_item
from logger import log_event


@safe_action
def corridor_access_puzzle(state: dict) -> bool:
    """
    Guess a number from 1 to 10 in 3 attempts.
    Returns True on success, False when the access panel resets.
    """
    secret = random.randint(1, 10)
    attempts = 3

    print("\n  The corridor access panel lights up.")
    print("  Guess the access number from 1 to 10. You have 3 guesses.")
    log_event("CHALLENGE_ATTEMPT", "Puzzle=CorridorAccess START")

    for attempt in range(1, attempts + 1):
        guess = prompt_menu_number(
            f"  Guess {attempt}/{attempts} (1-10): ",
            1,
            10
        )

        if guess == secret:
            print("  Correct. The corridor doors slide open.")
            log_event("CHALLENGE_ATTEMPT", "Puzzle=CorridorAccess", "SUCCESS")
            state["flags"]["corridor_access_granted"] = True
            return True

        if guess < secret:
            print("  Too low.")
        else:
            print("  Too high.")

        log_event(
            "CHALLENGE_ATTEMPT",
            f"Puzzle=CorridorAccess FAIL attempt={attempt}"
        )

    print("  Three wrong guesses. The panel resets with a new number.")
    log_event("CHALLENGE_ATTEMPT", "Puzzle=CorridorAccess RESET")
    return False


@safe_action
def terminal_puzzle(state: dict) -> bool:
    """
    Guess a 3-letter code in 3 attempts.
    Returns True on success, False on failure.
    """
    secret = random.choice(["zen", "ark", "ion", "sol", "tau"])
    
    if "AccessCode" in state["inventory"]:
        attempts = 40
    else:
        attempts = 20

    log_event("CHALLENGE_ATTEMPT", "Puzzle=TerminalLogin START")

    for i in range(1, attempts + 1):
        while True:
            try:
                raw = input(
                    f"\n  Terminal login {i}/{attempts} — enter 3-letter code: "
                ).strip().lower()

            except EOFError:
                raise InputError("Input stream closed during terminal puzzle.")

            if len(raw) == 3 and raw.isalpha():
                break

            print("  [Code must be exactly 3 letters, e.g. 'ark']")
            log_event("INPUT_INVALID", f'Terminal puzzle got "{raw}"')

        if raw == secret:
            print("  Access granted. You disabled an alarm zone.")
            log_event("CHALLENGE_ATTEMPT", "Puzzle=TerminalLogin", "SUCCESS")
            state["flags"]["alarm_disabled"] = True
            return True

        hint = []

        for a, b in zip(raw, secret):
            hint.append("✓" if a == b else ("~" if a in secret else "✗"))

        print("  Hint:", " ".join(hint), "  (✓=correct  ~=wrong position  ✗=not in code)")
        log_event("CHALLENGE_ATTEMPT", f"Puzzle=TerminalLogin FAIL attempt={i}")

    print("  Terminal locked. A security sweep has been triggered.")
    log_event("CHALLENGE_ATTEMPT", "Puzzle=TerminalLogin", "FAIL")
    state["flags"]["sweep_triggered"] = True

    return False


@safe_action
def corridor_encounter(state: dict) -> bool:
    """Drone encounter — fight, distract, or run."""
    print("\n  A hostile drone blocks your path.")
    log_event("CHALLENGE_ATTEMPT", "Encounter=Drone START")

    choice = get_input(
        "  Do you fight, distract, or run? (fight/distract/run): ",
        ["fight", "distract", "run"]
    )

    if choice == "fight":
        power = 0.5 + (0.2 if "Coin" in state["inventory"] else 0)

        if random.random() < power:
            print("  You disabled the drone.")
            log_event("CHALLENGE_ATTEMPT", "Encounter=Drone", "SUCCESS")
            return True

        print("  The drone damages you and you retreat.")
        log_event("CHALLENGE_ATTEMPT", "Encounter=Drone", "FAIL")
        state["flags"]["injured"] = True
        return False

    elif choice == "distract":
        if "Apple" in state["inventory"]:
            print("  You toss the apple — the drone tracks it and you slip past.")
            remove_item(state, "Apple")
            log_event("CHALLENGE_ATTEMPT", "Encounter=Drone", "SUCCESS")
            return True

        print("  Nothing to distract it with. It attacks.")
        log_event("CHALLENGE_ATTEMPT", "Encounter=Drone", "FAIL")
        state["flags"]["injured"] = True
        return False

    else:
        if random.random() < 0.6:
            print("  You outrun the drone.")
            log_event("CHALLENGE_ATTEMPT", "Encounter=Drone", "SUCCESS")
            return True

        print("  You fail to escape and are injured.")
        log_event("CHALLENGE_ATTEMPT", "Encounter=Drone", "FAIL")
        state["flags"]["injured"] = True
        return False
