import sys
import functools
from logger import log_event


class GameError(Exception):
    """Base game error."""


class InputError(GameError):
    """Player input was invalid or the input stream closed."""


class SaveError(GameError):
    """A save / load / delete file operation failed."""


class StateError(GameError):
    """Game state is missing required keys or is otherwise corrupt."""


def handle_error(error: Exception, *, fatal: bool = False) -> None:
    tag = "FATAL" if fatal else "WARNING"

    print(f"\n  [{tag} — {type(error).__name__}]: {error}\n")

    log_event(
        "ERROR",
        f"{type(error).__name__}: {error}",
        "FATAL" if fatal else "WARNING"
    )

    if fatal:
        print("  Your progress was saved at the last checkpoint.")
        sys.exit(1)


def safe_action(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except KeyboardInterrupt:
            print("\n\n  Interrupted — exiting. Progress saved at last checkpoint.")
            log_event("GAME_END", "KeyboardInterrupt", "EXIT")
            sys.exit(0)

        except GameError as e:
            handle_error(e)

        except Exception as e:
            handle_error(e, fatal=True)

    return wrapper