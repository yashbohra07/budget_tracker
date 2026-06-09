from datetime import datetime, timezone
from bson import ObjectId
from db import get_db


def _future_months(from_month: str, n: int = 11) -> list:
    """Returns from_month plus the next n months as 'YYYY-MM' strings."""
    year, mon = map(int, from_month.split("-"))
    result = []
    for i in range(n + 1):
        m, y = (mon + i - 1) % 12 + 1, year + (mon + i - 1) // 12
        result.append(f"{y}-{m:02d}")
    return result


def set_budget_cascading(month: str, category_id, amount: float, subcategory_id=None):
    """Sets budget for the given month and propagates to the next 11 months (12 total)."""
    for m in _future_months(month):
        set_budget(m, category_id, amount, subcategory_id)


def carry_forward_budgets(from_month: str, to_month: str):
    """
    Copies all budgets from from_month into to_month (and cascades forward).
    Used to pre-fill a month from the previous month's setup.
    """
    for b in get_budgets(from_month):
        set_budget_cascading(to_month, b["category_id"], b["amount"], b.get("subcategory_id"))


def set_budget(month: str, category_id, amount: float, subcategory_id=None):
    """Upserts a budget. month: 'YYYY-MM'"""
    db = get_db()
    cat_oid = ObjectId(category_id) if isinstance(category_id, str) else category_id
    sub_oid = (ObjectId(subcategory_id) if isinstance(subcategory_id, str) else subcategory_id) if subcategory_id else None

    db.budgets.update_one(
        {"month": month, "category_id": cat_oid, "subcategory_id": sub_oid},
        {"$set": {
            "amount": round(float(amount), 2),
            "created_at": datetime.now(timezone.utc),
        }},
        upsert=True,
    )


def get_budgets(month: str):
    """Returns all budgets for a given month."""
    db = get_db()
    return list(db.budgets.find({"month": month}))


def delete_budget(budget_id):
    db = get_db()
    db.budgets.delete_one({"_id": ObjectId(budget_id) if isinstance(budget_id, str) else budget_id})
