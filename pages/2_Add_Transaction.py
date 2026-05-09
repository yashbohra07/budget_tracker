import streamlit as st
from datetime import date
from models.category import get_all_categories, get_subcategories
from models.transaction import add_transaction
from config import PERSONS
from components.styles import apply_global_styles, C, page_header, PERSON_COLOR

st.set_page_config(page_title="Add Transaction", page_icon="➕", layout="centered")

if not st.session_state.get("authenticated"):
    st.switch_page("app.py")

apply_global_styles()
page_header("➕", "Add Transaction")

categories = get_all_categories()
if not categories:
    st.warning("No categories found. Go to Settings to set them up.")
    st.stop()

cat_map = {c["name"]: c for c in categories}
selected_cat_name = st.selectbox("Category", list(cat_map.keys()))
selected_cat = cat_map[selected_cat_name]

subcats = get_subcategories(category_id=selected_cat["_id"])
if not subcats:
    st.warning("No subcategories for this category. Add them in Settings.")
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

col1, col2 = st.columns(2)
with col1:
    amount = st.number_input("Amount (₹)", min_value=0.0, step=1.0, format="%.2f")
with col2:
    txn_date = st.date_input("Date", value=date.today())

st.html(f'<div style="font-size:0.9rem;font-weight:600;color:{C["text"]};margin-bottom:0.4rem">Paid by</div>')
paid_by = st.radio("Paid by", PERSONS, horizontal=True, label_visibility="collapsed")
notes = st.text_input("Notes (optional)", placeholder="e.g. Big Bazaar run")

st.html("<div style='height:0.5rem'></div>")

if st.button("Add Transaction", type="primary", use_container_width=True):
    if amount <= 0:
        st.error("Amount must be greater than 0.")
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
