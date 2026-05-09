import streamlit as st

# ── Palette ───────────────────────────────────────────────────────────────────
C = {
    "primary":   "#5C6BC0",   # indigo
    "yash":      "#3B82F6",   # blue
    "daksha":    "#EC4899",   # rose/pink
    "ok":        "#22C55E",   # green
    "warn":      "#F59E0B",   # amber
    "over":      "#EF4444",   # red
    "neutral":   "#94A3B8",   # slate
    "card":      "#FFFFFF",
    "bg":        "#F1F5F9",
    "border":    "#E2E8F0",
    "text":      "#1E293B",
    "muted":     "#64748B",
    "total":     "#7C3AED",   # violet for totals
}

PERSON_COLOR = {"Yash": C["yash"], "Daksha": C["daksha"]}
STATUS_COLOR = {"ok": C["ok"], "warn": C["warn"], "over": C["over"]}


def apply_global_styles():
    st.markdown(f"""
    <style>
    /* ── Page & layout ────────────────────────────────────── */
    .main .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 780px;
    }}

    /* ── Native metric cards ──────────────────────────────── */
    [data-testid="metric-container"] {{
        background: {C["card"]};
        border-radius: 14px;
        padding: 1rem 1.2rem 0.8rem;
        box-shadow: 0 1px 6px rgba(0,0,0,0.07);
        border-top: 3px solid {C["primary"]};
    }}

    /* ── Bordered containers ──────────────────────────────── */
    [data-testid="stVerticalBlockBorderWrapper"] > div {{
        border-radius: 12px !important;
        border: 1px solid {C["border"]} !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }}

    /* ── Expanders ────────────────────────────────────────── */
    [data-testid="stExpander"] {{
        border-radius: 12px !important;
        border: 1px solid {C["border"]} !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        background: {C["card"]};
    }}

    /* ── Tabs ─────────────────────────────────────────────── */
    button[data-baseweb="tab"] {{
        border-radius: 8px 8px 0 0;
        font-weight: 500;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {C["primary"]} !important;
    }}

    /* ── Primary buttons ──────────────────────────────────── */
    .stButton > button[kind="primary"] {{
        border-radius: 10px;
        font-weight: 600;
        padding: 0.45rem 1.4rem;
        background: {C["primary"]};
        border: none;
        letter-spacing: 0.02em;
    }}
    .stButton > button[kind="primary"]:hover {{
        background: #4A58B5;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(92,107,192,0.35);
    }}
    .stButton > button[kind="secondary"] {{
        border-radius: 10px;
        font-weight: 500;
    }}

    /* ── Selectbox & inputs ───────────────────────────────── */
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stNumberInput"] > div > div,
    [data-testid="stTextInput"] > div > div {{
        border-radius: 10px !important;
    }}

    /* ── Divider ──────────────────────────────────────────── */
    hr {{
        border-color: {C["border"]};
        margin: 1.2rem 0;
    }}

    /* ── Progress bar height & radius ─────────────────────── */
    [data-testid="stProgress"] > div {{
        border-radius: 99px;
        height: 10px;
        background: {C["border"]};
    }}
    [data-testid="stProgress"] > div > div {{
        border-radius: 99px;
    }}

    /* ── Sidebar ──────────────────────────────────────────── */
    section[data-testid="stSidebar"] {{
        background: #1E2A4A;
    }}
    section[data-testid="stSidebar"] * {{
        color: #CBD5E1 !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"] {{
        background: rgba(92,107,192,0.3) !important;
        border-radius: 8px;
    }}
    </style>
    """, unsafe_allow_html=True)


# ── HTML component helpers ────────────────────────────────────────────────────

def metric_cards(items: list):
    """
    items: [{"label": str, "value": str, "color": hex, "icon": emoji}, ...]
    Renders a row of styled stat cards.
    """
    cards_html = ""
    for item in items:
        color = item.get("color", C["primary"])
        icon = item.get("icon", "")
        sub_html = (
            f"<div style='font-size:0.78rem;color:{C['muted']};margin-top:0.25rem'>{item['sub']}</div>"
            if item.get("sub") else ""
        )
        cards_html += f"""
        <div style="background:{C['card']};border-radius:14px;padding:1rem 1.2rem 0.9rem;
                    box-shadow:0 2px 8px rgba(0,0,0,0.07);border-top:3px solid {color};
                    flex:1;min-width:0;">
            <div style="font-size:0.75rem;font-weight:600;color:{C['muted']};
                        text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.3rem">
                {icon} {item['label']}
            </div>
            <div style="font-size:1.6rem;font-weight:700;color:{C['text']};line-height:1.1">
                {item['value']}
            </div>
            {sub_html}
        </div>
        """
    st.html(f"""
    <div style="display:flex;gap:0.8rem;margin-bottom:0.5rem">
        {cards_html}
    </div>
    """)


def balance_card(balance: dict):
    """Renders the balance card."""
    if balance["settled"]:
        st.html(f"""
        <div style="background:linear-gradient(135deg,#DCFCE7,#D1FAE5);border-radius:14px;
                    padding:1.2rem 1.5rem;border-left:5px solid {C['ok']};
                    display:flex;align-items:center;gap:0.8rem;margin-bottom:0.5rem;">
            <span style="font-size:1.8rem">&#x2705;</span>
            <div>
                <div style="font-size:1rem;font-weight:700;color:#166534">All settled up!</div>
                <div style="font-size:0.8rem;color:#15803D">No outstanding balance</div>
            </div>
        </div>
        """)
    else:
        owes_color = PERSON_COLOR.get(balance["owes"], C["primary"])
        owed_color = PERSON_COLOR.get(balance["owed_to"], C["primary"])
        st.html(f"""
        <div style="background:linear-gradient(135deg,#FEF2F2,#FEE2E2);border-radius:14px;
                    padding:1.2rem 1.5rem;border-left:5px solid {C['over']};margin-bottom:0.75rem;">
            <div style="font-size:0.75rem;font-weight:600;color:{C['muted']};
                        text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.5rem">
                Outstanding Balance
            </div>
            <div style="font-size:1.1rem;color:{C['text']}">
                <span style="font-weight:700;color:{owes_color}">{balance['owes']}</span>
                <span style="color:{C['muted']}"> owes </span>
                <span style="font-weight:700;color:{owed_color}">{balance['owed_to']}</span>
                <span style="font-size:1.5rem;font-weight:800;color:{C['over']};margin-left:0.5rem">
                    &#x20B9;{balance['amount']:,.2f}
                </span>
            </div>
        </div>
        """)


def person_badge(name: str) -> str:
    """Returns HTML for an inline colored person badge."""
    color = PERSON_COLOR.get(name, C["neutral"])
    return (
        f'<span style="background:{color}22;color:{color};'
        f'font-weight:600;font-size:0.75rem;padding:2px 9px;'
        f'border-radius:99px;border:1px solid {color}55">{name}</span>'
    )


def budget_bar(label: str, spent: float, budget: float, pct: float, status: str):
    """Renders a colored budget progress bar."""
    bar_color = STATUS_COLOR.get(status, C["ok"])
    bar_width = min(pct, 100)
    remaining = budget - spent
    remaining_text = f"&#x20B9;{abs(remaining):,.0f} {'over' if remaining < 0 else 'left'}"
    icon = {"ok": "&#x1F7E2;", "warn": "&#x1F7E1;", "over": "&#x1F534;"}[status]

    st.html(f"""
    <div style="margin-bottom:0.9rem">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.3rem">
            <span style="font-size:0.88rem;font-weight:500;color:{C['text']}">{icon} {label}</span>
            <span style="font-size:0.78rem;color:{C['muted']}">
                &#x20B9;{spent:,.0f} / &#x20B9;{budget:,.0f}
                &nbsp;&middot;&nbsp;
                <span style="color:{bar_color};font-weight:600">{remaining_text}</span>
            </span>
        </div>
        <div style="background:{C['border']};border-radius:99px;height:9px;overflow:hidden">
            <div style="width:{bar_width}%;background:{bar_color};height:100%;border-radius:99px"></div>
        </div>
    </div>
    """)


def txn_row(date_str: str, cat: str, subcat: str, amount: float, paid_by: str, notes: str = ""):
    """Renders a styled transaction row."""
    badge = person_badge(paid_by)
    notes_html = f'<span style="color:{C["muted"]};font-size:0.78rem"> &middot; {notes}</span>' if notes else ""
    st.html(f"""
    <div style="background:{C['card']};border-radius:12px;padding:0.75rem 1rem;
                border:1px solid {C['border']};display:flex;align-items:center;
                gap:0.8rem;margin-bottom:0.5rem;">
        <div style="font-size:0.75rem;font-weight:600;color:{C['muted']};
                    min-width:48px;text-align:center;line-height:1.2">{date_str}</div>
        <div style="flex:1;min-width:0">
            <div style="font-size:0.88rem;font-weight:500;color:{C['text']};
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis">
                {cat} <span style="color:{C['muted']}">&rsaquo;</span> {subcat}
            </div>
            <div style="margin-top:0.15rem">{badge}{notes_html}</div>
        </div>
        <div style="font-size:1rem;font-weight:700;color:{C['text']};white-space:nowrap">
            &#x20B9;{amount:,.0f}
        </div>
    </div>
    """)


def page_header(icon: str, title: str, subtitle: str = ""):
    """Renders a styled page header."""
    sub_html = f'<div style="font-size:0.85rem;color:{C["muted"]};margin-top:0.2rem">{subtitle}</div>' if subtitle else ""
    st.html(f"""
    <div style="margin-bottom:1.2rem">
        <div style="font-size:1.75rem;font-weight:800;color:{C['text']};line-height:1.2">
            {icon} {title}
        </div>
        {sub_html}
    </div>
    """)


def section_title(title: str):
    st.html(
        f'<div style="font-size:0.95rem;font-weight:700;color:{C["muted"]};'
        f'text-transform:uppercase;letter-spacing:0.07em;'
        f'margin:1.2rem 0 0.6rem">{title}</div>'
    )
