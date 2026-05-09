import streamlit as st
from models.category import (
    get_all_categories, get_subcategories,
    add_category, update_category, delete_category,
    add_subcategory, update_subcategory, delete_subcategory,
)
from config import PERSONS
from components.styles import apply_global_styles, C, page_header, section_title, PERSON_COLOR

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="centered")

if not st.session_state.get("authenticated"):
    st.switch_page("app.py")

apply_global_styles()
page_header("⚙️", "Settings")

ASSIGNEE_OPTIONS = ["Neutral"] + PERSONS
ASSIGNEE_VALUE   = {"Neutral": None, "Yash": "Yash", "Daksha": "Daksha"}

def assignee_display(value):
    if not value:
        return "Neutral"
    return value

# ── Add Category ──────────────────────────────────────────────────────────────
section_title("Categories")

with st.form("add_category_form"):
    new_cat_name = st.text_input("New category name", placeholder="e.g. Travel")
    if st.form_submit_button("➕ Add Category", type="primary"):
        if new_cat_name.strip():
            add_category(new_cat_name)
            st.success(f"Added '{new_cat_name}'")
            st.rerun()
        else:
            st.error("Name cannot be empty.")

st.html("<div style='height:0.5rem'></div>")

# ── Category list ─────────────────────────────────────────────────────────────
categories = get_all_categories()

for cat in categories:
    cat_id = cat["_id"]
    subcats = get_subcategories(category_id=cat_id)

    # Build assignee summary for the expander label
    assigned_count = sum(1 for s in subcats if s.get("assignee"))
    label = f"{cat['name']}  ·  {len(subcats)} subcategories"

    with st.expander(label):

        # ── Rename / delete category ──────────────────────────────────────────
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            new_name = st.text_input("Category name", value=cat["name"],
                                     key=f"rename_cat_{cat_id}", label_visibility="collapsed")
        with col2:
            if st.button("Rename", key=f"btn_rename_cat_{cat_id}"):
                if new_name.strip() and new_name.strip() != cat["name"]:
                    update_category(cat_id, new_name)
                    st.rerun()
        with col3:
            if st.button("🗑️ Delete", key=f"del_cat_{cat_id}", type="secondary"):
                delete_category(cat_id)
                st.rerun()

        if subcats:
            st.html(
                f'<div style="font-size:0.78rem;font-weight:600;color:{C["muted"]};'
                f'text-transform:uppercase;letter-spacing:0.06em;margin:0.8rem 0 0.4rem">Subcategories</div>'
            )

        for sub in subcats:
            sub_id = sub["_id"]
            current_assignee_str = assignee_display(sub.get("assignee"))
            assignee_color = PERSON_COLOR.get(sub.get("assignee"), C["neutral"])

            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            with col1:
                sub_new_name = st.text_input(
                    "Name", value=sub["name"], key=f"subname_{sub_id}",
                    label_visibility="collapsed",
                )
            with col2:
                new_assignee_str = st.selectbox(
                    "Assignee",
                    ASSIGNEE_OPTIONS,
                    index=ASSIGNEE_OPTIONS.index(current_assignee_str),
                    key=f"assignee_{sub_id}",
                    label_visibility="collapsed",
                )
            with col3:
                if st.button("Save", key=f"save_sub_{sub_id}"):
                    update_subcategory(
                        sub_id,
                        name=sub_new_name if sub_new_name.strip() != sub["name"] else None,
                        assignee=ASSIGNEE_VALUE[new_assignee_str],
                    )
                    st.rerun()
            with col4:
                if st.button("✕", key=f"del_sub_{sub_id}"):
                    delete_subcategory(sub_id)
                    st.rerun()

        # ── Add subcategory ───────────────────────────────────────────────────
        st.html("<div style='height:0.3rem'></div>")
        with st.form(f"add_sub_{cat_id}"):
            col1, col2 = st.columns([3, 2])
            with col1:
                new_sub_name = st.text_input("New subcategory name", placeholder="e.g. Petrol")
            with col2:
                new_sub_assignee_str = st.selectbox("Assignee", ASSIGNEE_OPTIONS)
            if st.form_submit_button("Add Subcategory"):
                if new_sub_name.strip():
                    add_subcategory(new_sub_name, cat_id, ASSIGNEE_VALUE[new_sub_assignee_str])
                    st.rerun()
                else:
                    st.error("Name cannot be empty.")
