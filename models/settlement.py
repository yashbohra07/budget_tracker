from datetime import datetime, timezone
from db import get_db


def add_settlement(from_person: str, to_person: str, amount: float):
    """Logs a full settlement. from_person pays to_person."""
    db = get_db()
    result = db.settlements.insert_one({
        "date": datetime.now(timezone.utc),
        "from_person": from_person,
        "to_person": to_person,
        "amount": round(float(amount), 2),
        "created_at": datetime.now(timezone.utc),
    })
    return result.inserted_id


def get_settlements():
    """Returns all settlements, newest first."""
    db = get_db()
    return list(db.settlements.find().sort("date", -1))


def get_last_settlement_date():
    """Returns the datetime of the most recent settlement, or None."""
    db = get_db()
    last = db.settlements.find_one({}, sort=[("date", -1)])
    return last["date"] if last else None
