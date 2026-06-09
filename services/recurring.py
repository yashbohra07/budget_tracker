import calendar
from datetime import date, datetime, timezone
from config import RECURRING_TRANSACTIONS
from models.category import get_all_categories, get_subcategories
from models.budget import get_budgets
from models.transaction import get_transactions, add_transaction


def _build_sub_lookup():
    """Returns {(cat_name_lower, sub_name_lower): subcategory_doc}"""
    cats = {c["_id"]: c["name"].lower() for c in get_all_categories()}
    lookup = {}
    for s in get_subcategories():
        cat_name = cats.get(s["category_id"], "")
        lookup[(cat_name, s["name"].lower())] = s
    return lookup


def get_recurring_subcategory_ids() -> set:
    """Returns the set of subcategory _ids that are auto-filled (to block manual entry)."""
    lookup = _build_sub_lookup()
    ids = set()
    for cfg in RECURRING_TRANSACTIONS:
        key = (cfg["category"].lower(), cfg["subcategory"].lower())
        sub = lookup.get(key)
        if sub:
            ids.add(sub["_id"])
    return ids


def auto_fill_recurring():
    """
    Called once per session on app load. For the current month, creates any
    recurring transactions whose due date has passed and don't yet exist.
    Amount is taken from the subcategory's budget; paid_by from the assignee.
    Skips silently if budget not set or subcategory not found.
    """
    today = date.today()
    month = f"{today.year}-{today.month:02d}"
    last_day = calendar.monthrange(today.year, today.month)[1]

    lookup = _build_sub_lookup()

    sub_budget = {
        b["subcategory_id"]: b["amount"]
        for b in get_budgets(month)
        if b.get("subcategory_id")
    }

    month_txns = get_transactions(
        date_from=date(today.year, today.month, 1),
        date_to=date(today.year, today.month, last_day),
    )
    existing_subcat_ids = {str(t["subcategory_id"]) for t in month_txns}

    for cfg in RECURRING_TRANSACTIONS:
        key = (cfg["category"].lower(), cfg["subcategory"].lower())
        sub = lookup.get(key)
        if not sub:
            continue

        if str(sub["_id"]) in existing_subcat_ids:
            continue  # already recorded

        amount = sub_budget.get(sub["_id"])
        if not amount:
            continue  # no budget set — skip silently

        paid_by = sub.get("assignee")
        if not paid_by:
            continue  # neutral subcategory — no payer to infer

        day = last_day if cfg["day"] == "last" else cfg["day"]
        add_transaction(
            amount=amount,
            date=datetime(today.year, today.month, day, tzinfo=timezone.utc),
            category_id=sub["category_id"],
            subcategory_id=sub["_id"],
            paid_by=paid_by,
            notes="Auto-filled",
        )
