import datetime
from config import AUDIT_LOG


def log_event(event_type: str, message: str = "", result: str = "") -> None:
    """Append a timestamped line to the audit log. Never raises."""
    try:
        ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        parts = [ts, "-", event_type]

        if result:
            parts += ["-", result]

        if message:
            parts += ["-", message]

        with open(AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(" ".join(parts) + "\n")

    except OSError:
        pass