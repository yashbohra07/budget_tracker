from models.transaction import get_transactions
from models.settlement import get_last_settlement_date
from models.category import get_subcategory
from datetime import date


def compute_balance() -> dict:
    """
    Returns the outstanding balance since the last settlement.

    Result dict:
      {
        "owes": "Yash" | "Daksha" | None,
        "owed_to": "Yash" | "Daksha" | None,
        "amount": float,
        "settled": bool,
      }

    Logic: for assigned subcategories only —
      if assignee != paid_by → assignee owes paid_by that amount.
    Neutral subcategories are excluded from this calculation.
    """
    last_settled = get_last_settlement_date()

    filters = {}
    if last_settled:
        filters["date_from"] = last_settled.date() if hasattr(last_settled, "date") else last_settled

    txns = get_transactions(**filters)

    # balance > 0 → Yash owes Daksha
    # balance < 0 → Daksha owes Yash
    balance = 0.0

    for txn in txns:
        subcat = get_subcategory(txn["subcategory_id"])
        if not subcat or not subcat.get("assignee"):
            continue  # neutral — skip

        assignee = subcat["assignee"]
        paid_by = txn["paid_by"]

        if assignee == paid_by:
            continue  # correct person paid, no debt

        # wrong person paid
        if paid_by == "Daksha":
            balance += txn["amount"]   # Yash owes Daksha more
        else:
            balance -= txn["amount"]   # Daksha owes Yash more

    balance = round(balance, 2)

    if balance == 0:
        return {"owes": None, "owed_to": None, "amount": 0.0, "settled": True}
    elif balance > 0:
        return {"owes": "Yash", "owed_to": "Daksha", "amount": balance, "settled": False}
    else:
        return {"owes": "Daksha", "owed_to": "Yash", "amount": abs(balance), "settled": False}


def get_balance_transactions() -> list:
    """
    Returns transactions that make up the current balance — assigned subcategories
    where paid_by != assignee, since last settlement. Each item includes
    _subcat_name, _assignee, and _cat_name for display.
    """
    from models.category import get_all_categories
    last_settled = get_last_settlement_date()
    filters = {}
    if last_settled:
        filters["date_from"] = last_settled.date() if hasattr(last_settled, "date") else last_settled

    txns = get_transactions(**filters)
    cats = {c["_id"]: c["name"] for c in get_all_categories()}
    result = []
    for txn in txns:
        subcat = get_subcategory(txn["subcategory_id"])
        if not subcat or not subcat.get("assignee"):
            continue
        if subcat["assignee"] == txn["paid_by"]:
            continue
        result.append({
            **txn,
            "_subcat_name": subcat["name"],
            "_assignee": subcat["assignee"],
            "_cat_name": cats.get(txn["category_id"], "—"),
        })
    return result


def get_neutral_spends_since_settlement() -> list:
    """
    Returns transactions on neutral subcategories since last settlement.
    Used to surface informal split suggestions on the dashboard.
    """
    last_settled = get_last_settlement_date()

    filters = {}
    if last_settled:
        filters["date_from"] = last_settled.date() if hasattr(last_settled, "date") else last_settled

    txns = get_transactions(**filters)

    neutral = []
    for txn in txns:
        subcat = get_subcategory(txn["subcategory_id"])
        if subcat and not subcat.get("assignee"):
            neutral.append({**txn, "_subcat_name": subcat["name"]})

    return neutral
