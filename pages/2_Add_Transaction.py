import calendar
import streamlit as st
from datetime import date, datetime
from models.category import get_all_categories, get_subcategories
from models.transaction import add_transaction
from config import PERSONS
from services.recurring import get_recurring_subcategory_ids
from components.styles import apply_global_styles, C, page_header, PERSON_COLOR

st.set_page_config(page_title="Add Transaction", page_icon="➕", layout="centered")

if not st.session_state.get("authenticated"):
    st.switch_page("app.py")

apply_global_styles()
page_header("➕", "Add Transaction")


def _shift_month(d: date, n: int) -> date:
    """Shift date by n months (positive = forward, negative = backward)."""
    month = d.month + n
    year = d.year + (month - 1) // 12
    month = ((month - 1) % 12) + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


# ── Category & subcategory ────────────────────────────────────────────────────
categories = get_all_categories()
if not categories:
    st.warning("No categories found. Go to Settings to set them up.")
    st.stop()

cat_map = {c["name"]: c for c in categories}
selected_cat_name = st.selectbox("Category", list(cat_map.keys()))
selected_cat = cat_map[selected_cat_name]

recurring_ids = get_recurring_subcategory_ids()
subcats = [
    s for s in get_subcategories(category_id=selected_cat["_id"])
    if s["_id"] not in recurring_ids
]
if not subcats:
    st.warning("No subcategories available for manual entry in this category.")
    st.stop()

sub_map = {s["name"]: s for s in subcats}
selected_sub_name = st.selectbox("Subcategory", list(sub_map.keys()))
selected_sub = sub_map[selected_sub_name]

assignee = selected_sub.get("assignee")
if assignee:
    color = PERSON_COLOR.get(assignee, C["neutral"])
    st.html(
        f'<div style="font-size:0.8rem;color:{C["muted"]};margin-bottom:0.5rem">'
        f'Assigned to &nbsp;<span style="background:{color}22;color:{color};font-weight:600;'
        f'padding:2px 9px;border-radius:99px;border:1px solid {color}55">{assignee}</span></div>'
    )
else:
    st.html(
        f'<div style="font-size:0.8rem;color:{C["muted"]};margin-bottom:0.5rem">'
        f'<span style="background:{C["neutral"]}22;color:{C["neutral"]};font-weight:600;'
        f'padding:2px 9px;border-radius:99px;border:1px solid {C["neutral"]}55">Neutral</span>'
        f'&nbsp; No assigned payer</div>'
    )

# ── Amount, date, paid by, notes ──────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    amount = st.number_input("Amount (₹)", min_value=0.0, step=1.0, format="%.2f")
with col2:
    txn_date = st.date_input("Date", value=date.today())

st.html(f'<div style="font-size:0.9rem;font-weight:600;color:{C["text"]};margin-bottom:0.4rem">Paid by</div>')
paid_by = st.radio("Paid by", PERSONS, horizontal=True, label_visibility="collapsed")
notes = st.text_input("Notes (optional)", placeholder="e.g. Big Bazaar run")

# ── Split across months ───────────────────────────────────────────────────────
st.html("<div style='height:0.3rem'></div>")
with st.expander("🔀 Split across months"):
    split_dir = st.radio(
        "Split direction",
        ["No split", "Past months", "Future months"],
        horizontal=True,
        label_visibility="collapsed",
    )

    split_dates = []
    if split_dir != "No split":
        n = st.number_input("Number of months", min_value=2, max_value=24, value=2, step=1)
        per_amount = round(amount / n, 2) if amount > 0 else 0

        if split_dir == "Past months":
            split_dates = [_shift_month(txn_date, -(n - i)) for i in range(n)]
        else:
            split_dates = [_shift_month(txn_date, i) for i in range(n)]

        if amount > 0:
            rows = "".join(
                f'<div style="display:flex;justify-content:space-between;padding:0.3rem 0;'
                f'border-bottom:1px solid {C["border"]};font-size:0.85rem">'
                f'<span style="color:{C["text"]}">{d.strftime("%d %b %Y")}</span>'
                f'<span style="font-weight:600;color:{C["text"]}">&#x20B9;{per_amount:,.2f}</span>'
                f'</div>'
                for d in split_dates
            )
            st.html(f"""
            <div style="background:{C['bg']};border-radius:10px;padding:0.6rem 0.9rem;margin-top:0.4rem">
              <div style="font-size:0.75rem;font-weight:600;color:{C['muted']};
                          text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.4rem">
                Preview — {n} entries of &#x20B9;{per_amount:,.2f} each
              </div>
              {rows}
            </div>
            """)

st.html("<div style='height:0.5rem'></div>")

# ── Submit ────────────────────────────────────────────────────────────────────
if st.button("Add Transaction", type="primary", use_container_width=True):
    if amount <= 0:
        st.error("Amount must be greater than 0.")
    elif split_dates:
        n = len(split_dates)
        per_amount = round(amount / n, 2)
        for d in split_dates:
            add_transaction(
                amount=per_amount,
                date=d,
                category_id=selected_cat["_id"],
                subcategory_id=selected_sub["_id"],
                paid_by=paid_by,
                notes=f"{notes} (split {split_dates.index(d) + 1}/{n})" if notes else f"Split {split_dates.index(d) + 1}/{n}",
            )
        st.success(f"Added {n} entries of ₹{per_amount:,.2f} under {selected_cat_name} › {selected_sub_name}")
    else:
        add_transaction(
            amount=amount,
            date=txn_date,
            category_id=selected_cat["_id"],
            subcategory_id=selected_sub["_id"],
            paid_by=paid_by,
            notes=notes,
        )
        st.success(f"Added ₹{amount:,.2f} under {selected_cat_name} › {selected_sub_name}")
