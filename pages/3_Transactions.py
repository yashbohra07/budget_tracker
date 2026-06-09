import streamlit as st
from datetime import datetime, date
from models.transaction import get_transactions, update_transaction, delete_transaction
from models.category import get_all_categories, get_subcategories, get_subcategory
from config import PERSONS
from components.styles import apply_global_styles, C, page_header, person_badge, section_title

st.set_page_config(page_title="Transactions", page_icon="📋", layout="centered")

if not st.session_state.get("authenticated"):
    st.switch_page("app.py")

apply_global_styles()
page_header("📋", "Transactions")

# ── Filters ───────────────────────────────────────────────────────────────────
categories = get_all_categories()
cat_map = {c["name"]: c for c in categories}

with st.expander("🔍 Filters", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        filter_person = st.selectbox("Paid by", ["All"] + PERSONS)
    with col2:
        cat_options = ["All"] + [c["name"] for c in categories]
        filter_cat_name = st.selectbox("Category", cat_options)

    col3, col4 = st.columns(2)
    with col3:
        if filter_cat_name != "All":
            sub_list = get_subcategories(category_id=cat_map[filter_cat_name]["_id"])
            sub_options = ["All"] + [s["name"] for s in sub_list]
            sub_map = {s["name"]: s for s in sub_list}
        else:
            sub_options = ["All"]
            sub_map = {}
        filter_sub_name = st.selectbox(
            "Subcategory", sub_options,
            disabled=(filter_cat_name == "All"),
        )
    with col4:
        pass  # spacer to keep date inputs on their own row

    col5, col6 = st.columns(2)
    with col5:
        date_from = st.date_input("From", value=date(datetime.now().year, datetime.now().month, 1))
    with col6:
        date_to = st.date_input("To", value=date.today())

filters = {"date_from": date_from, "date_to": date_to}
if filter_person != "All":
    filters["paid_by"] = filter_person
if filter_cat_name != "All":
    filters["category_id"] = cat_map[filter_cat_name]["_id"]
if filter_sub_name != "All" and filter_sub_name in sub_map:
    filters["subcategory_id"] = sub_map[filter_sub_name]["_id"]

txns = get_transactions(**filters)

# ── Summary strip ─────────────────────────────────────────────────────────────
if txns:
    total = sum(t["amount"] for t in txns)
    st.html(
        f'<div style="font-size:0.85rem;color:{C["muted"]};margin-bottom:0.5rem">'
        f'<b style="color:{C["text"]}">{len(txns)}</b> transactions &nbsp;&middot;&nbsp; '
        f'Total <b style="color:{C["text"]}">&#x20B9;{total:,.2f}</b></div>'
    )
else:
    st.caption("No transactions found.")

# ── Transaction list ──────────────────────────────────────────────────────────
cats = {c["_id"]: c["name"] for c in categories}
subcats = {s["_id"]: s for s in get_subcategories()}

if "edit_txn_id" not in st.session_state:
    st.session_state.edit_txn_id = None

for txn in txns:
    txn_id = str(txn["_id"])
    sub = subcats.get(txn["subcategory_id"])
    sub_name = sub["name"] if sub else "—"
    cat_name = cats.get(txn["category_id"], "—")
    date_str = txn["date"].strftime("%d %b %Y") if hasattr(txn["date"], "strftime") else str(txn["date"])
    badge_html = person_badge(txn["paid_by"])
    notes_text = txn.get("notes", "")

    with st.container(border=True):
        col1, col2, col3 = st.columns([5, 2, 1])
        with col1:
            st.html(
                f'<div style="font-size:0.9rem;font-weight:600;color:{C["text"]}">'
                f'{cat_name} <span style="color:{C["muted"]}">&rsaquo;</span> {sub_name}</div>'
                f'<div style="margin-top:0.2rem;font-size:0.78rem;color:{C["muted"]}">'
                f'{date_str} &nbsp; {badge_html}'
                f'{"&nbsp;&middot;&nbsp;" + notes_text if notes_text else ""}</div>'
            )
        with col2:
            st.html(
                f'<div style="font-size:1rem;font-weight:700;color:{C["text"]};'
                f'text-align:right;padding-top:0.3rem">&#x20B9;{txn["amount"]:,.2f}</div>'
            )
        with col3:
            if st.button("✏️", key=f"edit_{txn_id}", help="Edit"):
                st.session_state.edit_txn_id = txn_id if st.session_state.edit_txn_id != txn_id else None
                st.rerun()
            if st.button("🗑️", key=f"del_{txn_id}", help="Delete"):
                delete_transaction(txn["_id"])
                st.rerun()

        if st.session_state.edit_txn_id == txn_id:
            st.divider()
            with st.form(key=f"form_{txn_id}"):
                c1, c2 = st.columns(2)
                with c1:
                    new_amount = st.number_input("Amount", value=float(txn["amount"]), min_value=0.0, step=1.0, format="%.2f")
                with c2:
                    new_date = st.date_input("Date", value=txn["date"].date() if hasattr(txn["date"], "date") else txn["date"])

                all_cats = get_all_categories()
                cat_names = [c["name"] for c in all_cats]
                current_cat_name = cats.get(txn["category_id"], cat_names[0])
                new_cat_name = st.selectbox("Category", cat_names,
                                            index=cat_names.index(current_cat_name) if current_cat_name in cat_names else 0)
                new_cat = next(c for c in all_cats if c["name"] == new_cat_name)

                sub_list = get_subcategories(category_id=new_cat["_id"])
                sub_names = [s["name"] for s in sub_list]
                current_sub_name = sub_name if new_cat_name == current_cat_name else sub_names[0]
                new_sub_name = st.selectbox("Subcategory", sub_names,
                                            index=sub_names.index(current_sub_name) if current_sub_name in sub_names else 0)
                new_sub = next(s for s in sub_list if s["name"] == new_sub_name)

                new_paid_by = st.radio("Paid by", PERSONS, index=PERSONS.index(txn["paid_by"]), horizontal=True)
                new_notes = st.text_input("Notes", value=txn.get("notes", ""))

                if st.form_submit_button("Save changes", type="primary"):
                    from datetime import datetime as dt
                    update_transaction(txn["_id"], {
                        "amount": new_amount,
                        "date": dt.combine(new_date, dt.min.time()),
                        "category_id": new_cat["_id"],
                        "subcategory_id": new_sub["_id"],
                        "paid_by": new_paid_by,
                        "notes": new_notes,
                    })
                    st.session_state.edit_txn_id = None
                    st.rerun()
