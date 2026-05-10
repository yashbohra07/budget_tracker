from datetime import datetime, timezone
from bson import ObjectId
from db import get_db


def add_transaction(amount: float, date, category_id, subcategory_id, paid_by: str, notes: str = ""):
    db = get_db()
    now = datetime.now(timezone.utc)
    result = db.transactions.insert_one({
        "amount": round(float(amount), 2),
        "date": datetime.combine(date, datetime.min.time()),
        "category_id": ObjectId(category_id) if isinstance(category_id, str) else category_id,
        "subcategory_id": ObjectId(subcategory_id) if isinstance(subcategory_id, str) else subcategory_id,
        "paid_by": paid_by,
        "notes": notes.strip(),
        "created_at": now,
        "updated_at": now,
    })
    return result.inserted_id


def get_transactions(paid_by=None, category_id=None, subcategory_id=None, date_from=None, date_to=None):
    db = get_db()
    query = {}
    if paid_by:
        query["paid_by"] = paid_by
    if category_id:
        query["category_id"] = ObjectId(category_id) if isinstance(category_id, str) else category_id
    if subcategory_id:
        query["subcategory_id"] = ObjectId(subcategory_id) if isinstance(subcategory_id, str) else subcategory_id
    if date_from or date_to:
        query["date"] = {}
        if date_from:
            query["date"]["$gte"] = datetime.combine(date_from, datetime.min.time())
        if date_to:
            query["date"]["$lte"] = datetime.combine(date_to, datetime.max.time())
    return list(db.transactions.find(query).sort("date", -1))


def get_transactions_for_month(month: str):
    """month: 'YYYY-MM'"""
    year, mon = map(int, month.split("-"))
    from calendar import monthrange
    last_day = monthrange(year, mon)[1]
    date_from = datetime(year, mon, 1)
    date_to = datetime(year, mon, last_day, 23, 59, 59)
    db = get_db()
    return list(db.transactions.find({"date": {"$gte": date_from, "$lte": date_to}}).sort("date", -1))


def update_transaction(txn_id, fields: dict):
    db = get_db()
    allowed = {"amount", "date", "category_id", "subcategory_id", "paid_by", "notes"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if "amount" in updates:
        updates["amount"] = round(float(updates["amount"]), 2)
    updates["updated_at"] = datetime.now(timezone.utc)
    db.transactions.update_one(
        {"_id": ObjectId(txn_id) if isinstance(txn_id, str) else txn_id},
        {"$set": updates},
    )


def delete_transaction(txn_id):
    db = get_db()
    db.transactions.delete_one({"_id": ObjectId(txn_id) if isinstance(txn_id, str) else txn_id})


def get_monthly_total(month: str, paid_by: str = None) -> float:
    """Returns total amount spent in a month, optionally filtered by person."""
    txns = get_transactions_for_month(month)
    if paid_by:
        txns = [t for t in txns if t["paid_by"] == paid_by]
    return round(sum(t["amount"] for t in txns), 2)
