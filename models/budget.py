from datetime import datetime, timezone
from bson import ObjectId
from db import get_db


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
