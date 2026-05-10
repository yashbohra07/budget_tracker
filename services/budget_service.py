from collections import defaultdict
from models.budget import get_budgets
from models.transaction import get_transactions_for_month
from models.category import get_all_categories, get_subcategories


def get_budget_totals(month: str) -> dict:
    """
    Returns total budget for the month and per-person budgets derived from
    subcategory assignees.
    {
        "total": float,
        "by_person": {"Yash": float, "Daksha": float, ...}
    }
    For each category, uses the category-level budget if set; otherwise sums
    its subcategory budgets (avoids double-counting).
    """
    budgets = get_budgets(month)
    if not budgets:
        return {"total": 0.0, "by_person": {}}

    all_subcats = {s["_id"]: s for s in get_subcategories()}

    cat_level = {}          # cat_id -> amount
    sub_level = defaultdict(float)   # cat_id -> sum of subcat budgets
    person_budgets = defaultdict(float)

    for b in budgets:
        cat_id = b["category_id"]
        sub_id = b.get("subcategory_id")
        if sub_id is None:
            cat_level[cat_id] = b["amount"]
        else:
            sub_level[cat_id] += b["amount"]
            assignee = all_subcats.get(sub_id, {}).get("assignee")
            if assignee:
                person_budgets[assignee] += b["amount"]

    total = 0.0
    for cat_id in set(cat_level) | set(sub_level):
        total += cat_level[cat_id] if cat_id in cat_level else sub_level[cat_id]

    return {"total": round(total, 2), "by_person": dict(person_budgets)}


def get_budget_status(month: str) -> list:
    """
    Returns a list of budget status rows for all budgets set in the given month.
    Each row:
      {
        "category_id": ...,
        "category_name": str,
        "subcategory_id": ... | None,
        "subcategory_name": str | None,
        "budget_amount": float,
        "spent": float,
        "remaining": float,
        "pct_used": float,       # 0–100+
        "status": "ok" | "warn" | "over",
      }
    """
    budgets = get_budgets(month)
    if not budgets:
        return []

    txns = get_transactions_for_month(month)

    # Pre-build lookup maps
    cats = {c["_id"]: c["name"] for c in get_all_categories()}
    subcats = {s["_id"]: s["name"] for s in get_subcategories()}

    # Aggregate spent amounts
    spent_by_cat = defaultdict(float)
    spent_by_subcat = defaultdict(float)
    for txn in txns:
        spent_by_cat[txn["category_id"]] += txn["amount"]
        spent_by_subcat[txn["subcategory_id"]] += txn["amount"]

    rows = []
    for b in budgets:
        cat_id = b["category_id"]
        sub_id = b.get("subcategory_id")

        if sub_id:
            spent = spent_by_subcat.get(sub_id, 0.0)
            sub_name = subcats.get(sub_id, "Unknown")
        else:
            spent = spent_by_cat.get(cat_id, 0.0)
            sub_name = None

        budget_amt = b["amount"]
        remaining = round(budget_amt - spent, 2)
        pct = round((spent / budget_amt * 100) if budget_amt > 0 else 0, 1)

        if pct >= 100:
            status = "over"
        elif pct >= 80:
            status = "warn"
        else:
            status = "ok"

        rows.append({
            "category_id": cat_id,
            "category_name": cats.get(cat_id, "Unknown"),
            "subcategory_id": sub_id,
            "subcategory_name": sub_name,
            "budget_amount": budget_amt,
            "spent": round(spent, 2),
            "remaining": remaining,
            "pct_used": pct,
            "status": status,
        })

    return sorted(rows, key=lambda r: r["pct_used"], reverse=True)
