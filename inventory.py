from logger import log_event


def add_item(state: dict, item: str) -> None:
    if item not in state["inventory"]:
        state["inventory"].append(item)
        log_event("ITEM_ACQUIRED", f"Item={item}")
        print(f"  You acquired: {item}")

    else:
        print(f"  You already have: {item}")


def remove_item(state: dict, item: str) -> bool:
    if item in state["inventory"]:
        state["inventory"].remove(item)
        log_event("ITEM_REMOVED", f"Item={item}")
        print(f"  You used/removed: {item}")
        return True

    return False


def show_inventory(state: dict) -> None:
    inv = state["inventory"]

    print("  Inventory:", ", ".join(inv) if inv else "(empty)")
    print("  Location :", state.get("location", "unknown"))

    active = {k: v for k, v in state.get("flags", {}).items() if v}

    if active:
        print("  Status   :", ", ".join(f"{k}={v}" for k, v in active.items()))