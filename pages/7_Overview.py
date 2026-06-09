import streamlit as st
from datetime import datetime
from models.category import get_all_categories, get_subcategories
from models.budget import get_budgets
from components.styles import apply_global_styles, C, PERSON_COLOR, page_header

st.set_page_config(page_title="Overview", page_icon="🗂️", layout="centered")

if not st.session_state.get("authenticated"):
    st.switch_page("app.py")

apply_global_styles()

# ── Header row ────────────────────────────────────────────────────────────────
now = datetime.now()
current_month = f"{now.year}-{now.month:02d}"

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
    page_header("🗂️", "Overview")
with col_month:
    st.write("")
    month = st.selectbox("Month", months, index=months.index(current_month),
                         label_visibility="collapsed")

# ── Load data ─────────────────────────────────────────────────────────────────
categories   = get_all_categories()
all_subcats  = get_subcategories()
budgets      = get_budgets(month)

cat_budget = {b["category_id"]: b["amount"] for b in budgets if not b.get("subcategory_id")}
sub_budget = {b["subcategory_id"]: b["amount"] for b in budgets if b.get("subcategory_id")}
subcats_by_cat = {}
for s in all_subcats:
    subcats_by_cat.setdefault(s["category_id"], []).append(s)

# Pre-compute per-assignee budget totals from subcategory budgets
person_totals = {"Yash": 0.0, "Daksha": 0.0, "Neutral": 0.0}
for s in all_subcats:
    amt = sub_budget.get(s["_id"], 0.0)
    key = s.get("assignee") or "Neutral"
    if key in person_totals:
        person_totals[key] += amt

# ── Assignee filter ───────────────────────────────────────────────────────────
FILTER_OPTIONS = ["All", "Yash", "Daksha", "Neutral"]
selected_filter = st.radio(
    "Filter by assignee",
    FILTER_OPTIONS,
    horizontal=True,
    label_visibility="collapsed",
)

st.html("<div style='height:0.3rem'></div>")

# ── Category cards ────────────────────────────────────────────────────────────
for cat in categories:
    cat_id  = cat["_id"]
    subcats = subcats_by_cat.get(cat_id, [])

    # Apply assignee filter
    if selected_filter == "Neutral":
        subcats = [s for s in subcats if not s.get("assignee")]
    elif selected_filter != "All":
        subcats = [s for s in subcats if s.get("assignee") == selected_filter]

    if not subcats and selected_filter != "All":
        continue  # hide categories with no matching subcategories

    budget = cat_budget.get(cat_id)
    budget_html = (
        f'<span style="font-size:0.8rem;color:{C["muted"]};font-weight:500">'
        f'Budget: <b style="color:{C["text"]}">&#x20B9;{budget:,.0f}</b></span>'
        if budget else
        f'<span style="font-size:0.78rem;color:{C["neutral"]}">No budget set</span>'
    )

    rows_html = ""
    for s in subcats:
        assignee   = s.get("assignee")
        color      = PERSON_COLOR.get(assignee, C["neutral"])
        label      = assignee or "Neutral"
        sub_bgt    = sub_budget.get(s["_id"])
        budget_str = f'&#x20B9;{sub_bgt:,.0f}' if sub_bgt else '—'
        rows_html += f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:0.5rem 1rem;border-bottom:1px solid {C['border']}">
          <span style="font-size:0.88rem;color:{C['text']}">{s['name']}</span>
          <div style="display:flex;align-items:center;gap:1rem">
            <span style="font-size:0.82rem;color:{C['muted']}">{budget_str}</span>
            <span style="background:{color}22;color:{color};font-size:0.75rem;font-weight:600;
                         padding:2px 9px;border-radius:99px;border:1px solid {color}55">{label}</span>
          </div>
        </div>
        """

    if not rows_html:
        rows_html = f'<div style="padding:0.6rem 1rem;font-size:0.82rem;color:{C["neutral"]}">No subcategories</div>'

    st.html(f"""
    <div style="background:{C['card']};border-radius:14px;border:1px solid {C['border']};
                box-shadow:0 1px 4px rgba(0,0,0,0.05);margin-bottom:0.8rem;overflow:hidden">
      <div style="background:{C['bg']};padding:0.7rem 1rem;
                  display:flex;justify-content:space-between;align-items:center;
                  border-bottom:1px solid {C['border']}">
        <span style="font-size:0.95rem;font-weight:700;color:{C['text']}">{cat['name']}</span>
        {budget_html}
      </div>
      {rows_html}
    </div>
    """)

# ── Budget total footer ───────────────────────────────────────────────────────
st.html("<div style='height:0.5rem'></div>")

if selected_filter == "All":
    cols_html = ""
    for person, total in person_totals.items():
        color = PERSON_COLOR.get(person, C["neutral"])
        cols_html += f"""
        <div style="flex:1;text-align:center;padding:0.8rem 0.5rem;
                    border-right:1px solid {C['border']}">
          <div style="font-size:0.75rem;font-weight:600;color:{C['muted']};
                      text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.3rem">
            <span style="color:{color}">{person}</span>
          </div>
          <div style="font-size:1.25rem;font-weight:700;color:{C['text']}">
            &#x20B9;{total:,.0f}
          </div>
        </div>
        """
    # remove trailing border on last item via CSS last-child would need JS; just strip manually
    st.html(f"""
    <div style="background:{C['card']};border-radius:14px;border:1px solid {C['border']};
                box-shadow:0 1px 6px rgba(0,0,0,0.06);overflow:hidden">
      <div style="background:{C['bg']};padding:0.5rem 1rem;font-size:0.78rem;font-weight:600;
                  color:{C['muted']};text-transform:uppercase;letter-spacing:0.06em;
                  border-bottom:1px solid {C['border']}">Total Budget by Assignee</div>
      <div style="display:flex">{cols_html}</div>
    </div>
    """)
else:
    total = person_totals.get(selected_filter, 0.0)
    color = PERSON_COLOR.get(selected_filter, C["neutral"])
    st.html(f"""
    <div style="background:{C['card']};border-radius:14px;border:1px solid {C['border']};
                box-shadow:0 1px 6px rgba(0,0,0,0.06);padding:0.9rem 1.2rem;
                display:flex;justify-content:space-between;align-items:center">
      <span style="font-size:0.88rem;font-weight:600;color:{C['muted']}">
        Total budget assigned to
        <span style="color:{color}">{selected_filter}</span>
      </span>
      <span style="font-size:1.4rem;font-weight:800;color:{C['text']}">
        &#x20B9;{total:,.0f}
      </span>
    </div>
    """)
