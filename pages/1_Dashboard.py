import streamlit as st
from datetime import datetime
from services.balance import compute_balance, get_neutral_spends_since_settlement, get_balance_transactions
from services.budget_service import get_budget_status, get_budget_totals
from models.transaction import get_transactions_for_month, get_monthly_total
from models.settlement import add_settlement
from models.category import get_subcategory, get_all_categories
from components.styles import (
    apply_global_styles, C, PERSON_COLOR, metric_cards, balance_card,
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
for i in range(11, -12, -1):  # 11 past + current + 11 future
    m = now.month - i
    y = now.year
    while m <= 0:
        m += 12
        y -= 1
    while m > 12:
        m -= 12
        y += 1
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
total        = get_monthly_total(month)
yash_total   = get_monthly_total(month, paid_by="Yash")
daksha_total = get_monthly_total(month, paid_by="Daksha")

budget_totals  = get_budget_totals(month)
total_budget   = budget_totals["total"]
yash_budget    = budget_totals["by_person"].get("Yash", 0)
daksha_budget  = budget_totals["by_person"].get("Daksha", 0)

def _spend_bar(label: str, color: str, spent: float, budget: float) -> str:
    pct       = round(min((spent / budget * 100) if budget > 0 else 0, 100), 1)
    bar_color = C["over"] if (budget and spent > budget) else color
    remaining = budget - spent if budget else None
    if budget:
        right = (
            f'<span style="color:{C["over"]};font-weight:600">&#x20B9;{spent - budget:,.0f} over</span>'
            if spent > budget else
            f'<span style="color:{C["ok"]};font-weight:600">&#x20B9;{remaining:,.0f} left</span>'
        )
        sub = f'&#x20B9;{spent:,.0f} <span style="color:{C["muted"]}">of &#x20B9;{budget:,.0f}</span> &nbsp;&middot;&nbsp; {right}'
    else:
        sub = f'&#x20B9;{spent:,.0f} <span style="color:{C["neutral"]};font-size:0.75rem">&nbsp;· no budget set</span>'
        pct = 0

    return f"""
    <div style="margin-bottom:1.1rem">
      <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:0.35rem">
        <span style="font-size:0.82rem;font-weight:700;color:{C['muted']};
                     text-transform:uppercase;letter-spacing:0.05em">{label}</span>
        <span style="font-size:0.82rem;color:{C['text']}">{sub}</span>
      </div>
      <div style="background:{C['border']};border-radius:99px;height:10px;overflow:hidden">
        <div style="width:{pct}%;background:{bar_color};height:100%;border-radius:99px;
                    transition:width 0.4s ease"></div>
      </div>
    </div>
    """

st.html(f"""
<div style="background:{C['card']};border-radius:14px;padding:1.2rem 1.4rem 0.4rem;
            box-shadow:0 2px 8px rgba(0,0,0,0.07);border-top:3px solid {C['total']};
            margin-bottom:0.5rem">
  {_spend_bar("💸 Total", C["total"], total, total_budget)}
  {_spend_bar("👤 Yash",   C["yash"],   yash_total,   yash_budget)}
  {_spend_bar("👤 Daksha", C["daksha"], daksha_total, daksha_budget)}
</div>
""")

st.html("<div style='height:0.5rem'></div>")

# ── Balance ───────────────────────────────────────────────────────────────────
section_title("Balance")
balance = compute_balance()
balance_card(balance)

if not balance["settled"]:
    bal_txns = get_balance_transactions()
    if bal_txns:
        with st.expander(f"📋 Breakdown  ({len(bal_txns)} transactions)"):
            for t in bal_txns:
                date_str = t["date"].strftime("%d %b %Y") if hasattr(t["date"], "strftime") else str(t["date"])
                paid_color = PERSON_COLOR.get(t["paid_by"], C["neutral"])
                assignee_color = PERSON_COLOR.get(t["_assignee"], C["neutral"])
                st.html(
                    f'<div style="display:flex;justify-content:space-between;align-items:center;'
                    f'padding:0.4rem 0;border-bottom:1px solid {C["border"]}">'
                    f'  <div>'
                    f'    <div style="font-size:0.88rem;font-weight:500;color:{C["text"]}">'
                    f'      {t["_cat_name"]} <span style="color:{C["muted"]}">&rsaquo;</span> {t["_subcat_name"]}'
                    f'    </div>'
                    f'    <div style="font-size:0.75rem;color:{C["muted"]};margin-top:0.15rem">'
                    f'      {date_str} &nbsp;&middot;&nbsp; '
                    f'      paid by <span style="color:{paid_color};font-weight:600">{t["paid_by"]}</span>'
                    f'      &nbsp;&middot;&nbsp; assigned to '
                    f'      <span style="color:{assignee_color};font-weight:600">{t["_assignee"]}</span>'
                    f'    </div>'
                    f'  </div>'
                    f'  <div style="font-size:0.95rem;font-weight:700;color:{C["text"]};white-space:nowrap;margin-left:1rem">'
                    f'    &#x20B9;{t["amount"]:,.0f}'
                    f'  </div>'
                    f'</div>'
                )

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
    from collections import defaultdict
    by_cat = defaultdict(lambda: {"cat_row": None, "sub_rows": [], "cat_name": ""})
    for row in budget_rows:
        cid = row["category_id"]
        by_cat[cid]["cat_name"] = row["category_name"]
        if row["subcategory_id"] is None:
            by_cat[cid]["cat_row"] = row
        else:
            by_cat[cid]["sub_rows"].append(row)

    STATUS_ICON = {"ok": "🟢", "warn": "🟡", "over": "🔴"}

    for cid, data in by_cat.items():
        cat_row  = data["cat_row"]
        sub_rows = data["sub_rows"]
        cat_name = data["cat_name"]

        if cat_row:
            spent, budget, pct, status = cat_row["spent"], cat_row["budget_amount"], cat_row["pct_used"], cat_row["status"]
        elif sub_rows:
            spent  = sum(r["spent"] for r in sub_rows)
            budget = sum(r["budget_amount"] for r in sub_rows)
            pct    = round((spent / budget * 100) if budget > 0 else 0, 1)
            status = "over" if pct >= 100 else "warn" if pct >= 80 else "ok"
        else:
            continue

        if sub_rows:
            label = f"{STATUS_ICON[status]}  {cat_name}   ₹{spent:,.0f} / ₹{budget:,.0f}"
            with st.expander(label):
                for sub in sub_rows:
                    budget_bar(sub["subcategory_name"], sub["spent"], sub["budget_amount"], sub["pct_used"], sub["status"])
        else:
            budget_bar(cat_name, spent, budget, pct, status)

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
