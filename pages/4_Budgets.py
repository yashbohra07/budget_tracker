import streamlit as st
from datetime import datetime
from models.budget import set_budget, get_budgets, delete_budget
from models.category import get_all_categories, get_subcategories
from services.budget_service import get_budget_status
from components.styles import apply_global_styles, C, page_header, budget_bar, section_title

st.set_page_config(page_title="Budgets", page_icon="🎯", layout="centered")

if not st.session_state.get("authenticated"):
    st.switch_page("app.py")

apply_global_styles()

now = datetime.now()
months = []
for i in range(11, -1, -1):
    m = now.month - i
    y = now.year
    while m <= 0:
        m += 12
        y -= 1
    months.append(f"{y}-{m:02d}")

current_month = f"{now.year}-{now.month:02d}"

col_title, col_month = st.columns([2, 1])
with col_title:
    page_header("🎯", "Budgets")
with col_month:
    st.write("")
    month = st.selectbox("Month", months, index=months.index(current_month), label_visibility="collapsed")

# ── Budget vs Actual ──────────────────────────────────────────────────────────
section_title("Budget vs Actual")
rows = get_budget_status(month)

if not rows:
    st.caption("No budgets set for this month.")
else:
    for row in rows:
        label = row["category_name"]
        if row["subcategory_name"]:
            label += f" › {row['subcategory_name']}"
        budget_bar(label, row["spent"], row["budget_amount"], row["pct_used"], row["status"])

st.divider()

# ── Set / edit budgets ────────────────────────────────────────────────────────
section_title("Set Budgets")
categories = get_all_categories()
existing = {
    (str(b["category_id"]), str(b["subcategory_id"]) if b.get("subcategory_id") else None): b
    for b in get_budgets(month)
}

for cat in categories:
    cat_id = cat["_id"]
    cat_key = (str(cat_id), None)

    with st.expander(cat["name"]):
        existing_cat_budget = existing.get(cat_key)
        current_val = float(existing_cat_budget["amount"]) if existing_cat_budget else 0.0

        col1, col2 = st.columns([3, 1])
        with col1:
            new_val = st.number_input(
                f"{cat['name']} (overall)",
                min_value=0.0, step=500.0, format="%.0f",
                value=current_val, key=f"cat_{cat_id}",
            )
        with col2:
            st.write("")
            st.write("")
            if st.button("Save", key=f"save_cat_{cat_id}"):
                if new_val > 0:
                    set_budget(month, cat_id, new_val)
                elif existing_cat_budget:
                    delete_budget(existing_cat_budget["_id"])
                st.rerun()

        subcats = get_subcategories(category_id=cat_id)
        for sub in subcats:
            sub_id = sub["_id"]
            sub_key = (str(cat_id), str(sub_id))
            existing_sub_budget = existing.get(sub_key)
            current_sub_val = float(existing_sub_budget["amount"]) if existing_sub_budget else 0.0

            col1, col2 = st.columns([3, 1])
            with col1:
                new_sub_val = st.number_input(
                    f"  › {sub['name']}",
                    min_value=0.0, step=100.0, format="%.0f",
                    value=current_sub_val, key=f"sub_{sub_id}",
                )
            with col2:
                st.write("")
                st.write("")
                if st.button("Save", key=f"save_sub_{sub_id}"):
                    if new_sub_val > 0:
                        set_budget(month, cat_id, new_sub_val, subcategory_id=sub_id)
                    elif existing_sub_budget:
                        delete_budget(existing_sub_budget["_id"])
                    st.rerun()
