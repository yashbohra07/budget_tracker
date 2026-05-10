import streamlit as st
from datetime import datetime
from services.balance import compute_balance, get_neutral_spends_since_settlement
from services.budget_service import get_budget_status
from models.transaction import get_transactions_for_month, get_monthly_total
from models.settlement import add_settlement
from models.category import get_subcategory, get_all_categories
from components.styles import (
    apply_global_styles, C, metric_cards, balance_card,
    budget_bar, txn_row, page_header, section_title, person_badge,
)

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="centered")

if not st.session_state.get("authenticated"):
    st.switch_page("app.py")

apply_global_styles()

# ── Month selector ────────────────────────────────────────────────────────────
now = datetime.now()
current_month = f"{now.year}-{now.month:02d}"
if "selected_month" not in st.session_state:
    st.session_state.selected_month = current_month

months = []
for i in range(11, -1, -1):
    m = now.month - i
    y = now.year
    while m <= 0:
        m += 12
        y -= 1
    months.append(f"{y}-{m:02d}")

col_title, col_month = st.columns([2, 1])
with col_title:
    page_header("🏠", "Dashboard")
with col_month:
    st.write("")
    selected = st.selectbox("Month", months, index=months.index(current_month),
                            key="dashboard_month", label_visibility="collapsed")
st.session_state.selected_month = selected
month = selected

# ── Spend summary ─────────────────────────────────────────────────────────────
total       = get_monthly_total(month)
yash_total  = get_monthly_total(month, paid_by="Yash")
daksha_total= get_monthly_total(month, paid_by="Daksha")

metric_cards([
    {"label": "Total Spent",  "value": f"₹{total:,.0f}",        "color": C["total"],  "icon": "💸"},
    {"label": "Yash",         "value": f"₹{yash_total:,.0f}",   "color": C["yash"],   "icon": "👤"},
    {"label": "Daksha",       "value": f"₹{daksha_total:,.0f}", "color": C["daksha"], "icon": "👤"},
])

st.html("<div style='height:0.5rem'></div>")

# ── Balance ───────────────────────────────────────────────────────────────────
section_title("Balance")
balance = compute_balance()
balance_card(balance)

if not balance["settled"]:
    if st.button("Settle Now", type="primary"):
        add_settlement(
            from_person=balance["owes"],
            to_person=balance["owed_to"],
            amount=balance["amount"],
        )
        st.success("Settled! Balance reset.")
        st.rerun()

# ── Neutral spends callout ────────────────────────────────────────────────────
neutral = get_neutral_spends_since_settlement()
if neutral:
    total_neutral = sum(t["amount"] for t in neutral)
    with st.expander(f"💬 Unassigned spends since last settlement — ₹{total_neutral:,.0f}  *(consider splitting)*"):
        for t in neutral:
            date_str = t["date"].strftime("%d %b") if hasattr(t["date"], "strftime") else str(t["date"])
            st.html(
                f'<div style="font-size:0.85rem;color:{C["text"]};padding:0.1rem 0">'
                f'&nbsp;&nbsp;{date_str} &nbsp;&middot;&nbsp; {t["_subcat_name"]} &nbsp;&middot;&nbsp; '
                f'&#x20B9;{t["amount"]:,.0f} &nbsp;&middot;&nbsp; {person_badge(t["paid_by"])}</div>'
            )

st.html("<div style='height:0.3rem'></div>")

# ── Budget health ─────────────────────────────────────────────────────────────
section_title("Budget Health")
budget_rows = get_budget_status(month)

if not budget_rows:
    st.caption("No budgets set for this month. Set them in the Budgets page.")
else:
    for row in budget_rows:
        label = row["category_name"]
        if row["subcategory_name"]:
            label += f" › {row['subcategory_name']}"
        budget_bar(label, row["spent"], row["budget_amount"], row["pct_used"], row["status"])

# ── Recent transactions ───────────────────────────────────────────────────────
section_title("Recent Transactions")
txns = get_transactions_for_month(month)[:5]

if not txns:
    st.caption("No transactions this month.")
else:
    cats = {c["_id"]: c["name"] for c in get_all_categories()}
    for txn in txns:
        sub = get_subcategory(txn["subcategory_id"])
        sub_name = sub["name"] if sub else "—"
        cat_name = cats.get(txn["category_id"], "—")
        date_str = txn["date"].strftime("%d %b") if hasattr(txn["date"], "strftime") else str(txn["date"])
        txn_row(date_str, cat_name, sub_name, txn["amount"], txn["paid_by"], txn.get("notes", ""))
