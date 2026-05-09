from collections import defaultdict
from models.transaction import get_transactions_for_month, get_transactions
from models.category import get_subcategory, get_all_categories, get_subcategories
from datetime import datetime
from calendar import monthrange


def spending_by_category(month: str) -> dict:
    """Returns {category_name: total_amount} for the given month."""
    txns = get_transactions_for_month(month)
    cats = {str(c["_id"]): c["name"] for c in get_all_categories()}

    totals = defaultdict(float)
    for txn in txns:
        cat_name = cats.get(str(txn["category_id"]), "Unknown")
        totals[cat_name] += txn["amount"]

    return dict(sorted(totals.items(), key=lambda x: x[1], reverse=True))


def spending_by_subcategory(month: str, category_id=None) -> dict:
    """Returns {subcategory_name: total_amount}. Optionally filtered by category."""
    txns = get_transactions_for_month(month)
    if category_id:
        from bson import ObjectId
        oid = ObjectId(category_id) if isinstance(category_id, str) else category_id
        txns = [t for t in txns if t["category_id"] == oid]

    subcats = {str(s["_id"]): s["name"] for s in get_subcategories()}
    totals = defaultdict(float)
    for txn in txns:
        sub_name = subcats.get(str(txn["subcategory_id"]), "Unknown")
        totals[sub_name] += txn["amount"]

    return dict(sorted(totals.items(), key=lambda x: x[1], reverse=True))


def spending_by_person(month: str) -> dict:
    """Returns {"Yash": total, "Daksha": total}."""
    txns = get_transactions_for_month(month)
    totals = defaultdict(float)
    for txn in txns:
        totals[txn["paid_by"]] += txn["amount"]
    return dict(totals)


def monthly_totals(n_months: int = 6) -> list:
    """
    Returns last n_months of spending totals.
    Result: [{"month": "YYYY-MM", "total": float, "Yash": float, "Daksha": float}, ...]
    """
    now = datetime.now()
    results = []

    for i in range(n_months - 1, -1, -1):
        month_dt = datetime(now.year, now.month, 1)
        # subtract i months
        total_months = now.month - 1 - i
        year = now.year + total_months // 12
        month = total_months % 12 + 1
        month_str = f"{year}-{month:02d}"

        txns = get_transactions_for_month(month_str)
        total = sum(t["amount"] for t in txns)
        yash = sum(t["amount"] for t in txns if t["paid_by"] == "Yash")
        daksha = sum(t["amount"] for t in txns if t["paid_by"] == "Daksha")

        results.append({
            "month": month_str,
            "total": round(total, 2),
            "Yash": round(yash, 2),
            "Daksha": round(daksha, 2),
        })

    return results
