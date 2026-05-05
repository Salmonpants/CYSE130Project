from errors import InputError
from logger import log_event


def get_input(prompt: str, valid: list[str]) -> str:
    valid_lower = [v.lower() for v in valid]
    display = " / ".join(valid)

    while True:
        try:
            raw = input(prompt).strip().lower()

        except EOFError:
            raise InputError(f"Input stream closed — expected one of: {display}")

        if raw in valid_lower:
            return raw

        log_event("INPUT_INVALID", f'Got "{raw}" — expected one of: {display}')
        print(f"  [Invalid input '{raw}'. Please enter one of: {display}]")


def prompt_menu_number(prompt: str, min_val: int, max_val: int) -> int:
    while True:
        try:
            raw = input(prompt).strip()
            num = int(raw)

            if min_val <= num <= max_val:
                return num

            log_event("INPUT_INVALID", f'Got "{raw}" — expected {min_val}–{max_val}')
            print(f"  [Please enter a number from {min_val} to {max_val}.]")

        except ValueError:
            log_event("INPUT_INVALID", f'Non-integer "{raw}" at numeric menu')
            print(f"  [Please enter a number from {min_val} to {max_val}.]")

        except EOFError:
            raise InputError("Input stream closed at menu.")