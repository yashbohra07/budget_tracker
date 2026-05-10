import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from services.analytics import (
    spending_by_category,
    spending_by_person,
    monthly_totals,
    spending_by_subcategory,
)
from services.budget_service import get_budget_status
from models.settlement import get_settlements
from components.styles import apply_global_styles, C, page_header, person_badge, section_title

st.set_page_config(page_title="Analytics", page_icon="📊", layout="centered")

if not st.session_state.get("authenticated"):
    st.switch_page("app.py")

apply_global_styles()
page_header("📊", "Analytics")

CHART_COLORS = [
    "#5C6BC0", "#EC4899", "#F59E0B", "#22C55E",
    "#3B82F6", "#EF4444", "#8B5CF6", "#14B8A6",
    "#F97316", "#06B6D4", "#84CC16", "#A855F7",
]

def base_layout(**kwargs):
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12, color=C["text"]),
        margin=dict(t=20, b=20, l=10, r=10),
        hoverlabel=dict(
            bgcolor=C["card"],
            bordercolor=C["border"],
            font=dict(size=12, color=C["text"]),
        ),
        **kwargs,
    )

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

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🍩 Categories",
    "📊 Breakdown",
    "📈 Trends",
    "🎯 Budget",
    "🤝 Settlements",
])

# ── Tab 1: Category Donut ─────────────────────────────────────────────────────
with tab1:
    month = st.selectbox("Month", months, index=months.index(current_month), key="t1_month")
    cat_data = spending_by_category(month)
    person_data = spending_by_person(month)

    if not cat_data:
        st.caption("No data for this month.")
    else:
        # ── Donut ──────────────────────────────────────────────────────────────
        labels = list(cat_data.keys())
        values = list(cat_data.values())
        total  = sum(values)

        fig = go.Figure(go.Pie(
            labels=labels,
            values=values,
            hole=0.6,
            direction="clockwise",
            sort=True,
            marker=dict(
                colors=CHART_COLORS[:len(labels)],
                line=dict(color=C["bg"], width=2),
            ),
            textposition="outside",
            textinfo="label+percent",
            textfont=dict(size=11),
            hovertemplate="<b>%{label}</b><br>&#x20B9;%{value:,.0f}<br>%{percent}<extra></extra>",
        ))
        fig.add_annotation(
            text=f"<b>&#x20B9;{total:,.0f}</b><br><span style='font-size:10px'>Total</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color=C["text"]),
            xanchor="center",
        )
        fig.update_layout(
            **base_layout(),
            showlegend=False,
            height=380,
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── Person split below donut ───────────────────────────────────────────
        if person_data:
            yash_amt   = person_data.get("Yash", 0)
            daksha_amt = person_data.get("Daksha", 0)
            combined   = yash_amt + daksha_amt or 1

            yash_pct   = yash_amt / combined * 100
            daksha_pct = daksha_amt / combined * 100

            st.html(f"""
            <div style="background:{C['card']};border-radius:14px;padding:1rem 1.2rem;
                        border:1px solid {C['border']};margin-top:0.5rem">
                <div style="font-size:0.75rem;font-weight:600;color:{C['muted']};
                            text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.8rem">
                    Who spent what
                </div>
                <div style="display:flex;gap:0.5rem;align-items:center;margin-bottom:0.5rem">
                    <span style="font-size:0.82rem;font-weight:600;color:{C['yash']};min-width:60px">Yash</span>
                    <div style="flex:1;background:{C['border']};border-radius:99px;height:10px;overflow:hidden">
                        <div style="width:{yash_pct:.1f}%;background:{C['yash']};height:100%;border-radius:99px"></div>
                    </div>
                    <span style="font-size:0.82rem;font-weight:700;color:{C['text']};min-width:72px;text-align:right">
                        &#x20B9;{yash_amt:,.0f}
                    </span>
                </div>
                <div style="display:flex;gap:0.5rem;align-items:center">
                    <span style="font-size:0.82rem;font-weight:600;color:{C['daksha']};min-width:60px">Daksha</span>
                    <div style="flex:1;background:{C['border']};border-radius:99px;height:10px;overflow:hidden">
                        <div style="width:{daksha_pct:.1f}%;background:{C['daksha']};height:100%;border-radius:99px"></div>
                    </div>
                    <span style="font-size:0.82rem;font-weight:700;color:{C['text']};min-width:72px;text-align:right">
                        &#x20B9;{daksha_amt:,.0f}
                    </span>
                </div>
            </div>
            """)

# ── Tab 2: Subcategory Breakdown ──────────────────────────────────────────────
with tab2:
    month2 = st.selectbox("Month", months, index=months.index(current_month), key="t2_month")
    sub_data = spending_by_subcategory(month2)

    if not sub_data:
        st.caption("No data for this month.")
    else:
        df = pd.DataFrame({
            "Subcategory": list(sub_data.keys()),
            "Amount": list(sub_data.values()),
        }).sort_values("Amount", ascending=True)

        # Assign colors based on rank
        n = len(df)
        bar_colors = [CHART_COLORS[i % len(CHART_COLORS)] for i in range(n)]

        fig = go.Figure(go.Bar(
            x=df["Amount"],
            y=df["Subcategory"],
            orientation="h",
            marker=dict(
                color=bar_colors,
                line=dict(width=0),
            ),
            text=[f"  &#x20B9;{v:,.0f}" for v in df["Amount"]],
            textposition="outside",
            textfont=dict(size=11, color=C["text"]),
            hovertemplate="<b>%{y}</b><br>&#x20B9;%{x:,.0f}<extra></extra>",
        ))
        fig.update_layout(
            **base_layout(),
            xaxis=dict(
                showgrid=True, gridcolor=C["border"],
                showticklabels=False, title="",
                zeroline=False,
            ),
            yaxis=dict(title="", tickfont=dict(size=11)),
            height=max(320, n * 34),
            bargap=0.35,
        )
        st.plotly_chart(fig, use_container_width=True)

# ── Tab 3: Monthly Trend ──────────────────────────────────────────────────────
with tab3:
    n_months = st.slider("Months to show", min_value=3, max_value=12, value=6, step=1)
    trend = monthly_totals(n_months=n_months)

    if not trend or all(t["total"] == 0 for t in trend):
        st.caption("No trend data yet.")
    else:
        df = pd.DataFrame(trend)

        fig = go.Figure()

        # Filled area for total
        fig.add_trace(go.Scatter(
            x=df["month"], y=df["total"],
            name="Total",
            mode="lines+markers",
            line=dict(color=C["total"], width=2.5, shape="spline"),
            marker=dict(size=8, color=C["total"], line=dict(color="white", width=2)),
            fill="tozeroy",
            fillcolor=f"rgba(124,58,237,0.08)",
            hovertemplate="<b>%{x}</b><br>Total: &#x20B9;%{y:,.0f}<extra></extra>",
        ))
        # Yash line
        fig.add_trace(go.Scatter(
            x=df["month"], y=df["Yash"],
            name="Yash",
            mode="lines+markers",
            line=dict(color=C["yash"], width=2, shape="spline", dash="dot"),
            marker=dict(size=6, color=C["yash"], line=dict(color="white", width=1.5)),
            hovertemplate="<b>%{x}</b><br>Yash: &#x20B9;%{y:,.0f}<extra></extra>",
        ))
        # Daksha line
        fig.add_trace(go.Scatter(
            x=df["month"], y=df["Daksha"],
            name="Daksha",
            mode="lines+markers",
            line=dict(color=C["daksha"], width=2, shape="spline", dash="dot"),
            marker=dict(size=6, color=C["daksha"], line=dict(color="white", width=1.5)),
            hovertemplate="<b>%{x}</b><br>Daksha: &#x20B9;%{y:,.0f}<extra></extra>",
        ))

        fig.update_layout(
            **base_layout(),
            xaxis=dict(
                showgrid=False, title="",
                tickfont=dict(size=11),
                fixedrange=True,
            ),
            yaxis=dict(
                showgrid=True, gridcolor=C["border"],
                title="Amount (&#x20B9;)",
                zeroline=False,
                tickprefix="₹",
                tickformat=",.0f",
            ),
            legend=dict(
                orientation="h", y=1.08, x=0.5, xanchor="center",
                bgcolor="rgba(0,0,0,0)", font=dict(size=11),
            ),
            height=340,
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

        # Month-over-month delta table
        if len(df) >= 2:
            section_title("Month-over-Month Change")
            rows_html = ""
            for i in range(1, len(df)):
                prev = df.iloc[i - 1]["total"]
                curr = df.iloc[i]["total"]
                delta = curr - prev
                pct   = (delta / prev * 100) if prev else 0
                arrow = "&#x2197;" if delta > 0 else "&#x2198;"
                color = C["over"] if delta > 0 else C["ok"]
                rows_html += f"""
                <tr>
                    <td style="padding:0.4rem 0.6rem;color:{C['muted']};font-size:0.82rem">{df.iloc[i]['month']}</td>
                    <td style="padding:0.4rem 0.6rem;font-weight:600">&#x20B9;{curr:,.0f}</td>
                    <td style="padding:0.4rem 0.6rem;color:{color};font-weight:600">
                        {arrow} &#x20B9;{abs(delta):,.0f} ({abs(pct):.1f}%)
                    </td>
                </tr>
                """
            st.html(f"""
            <table style="width:100%;border-collapse:collapse;font-size:0.85rem;
                          background:{C['card']};border-radius:12px;overflow:hidden;
                          border:1px solid {C['border']}">
                <thead>
                    <tr style="background:{C['bg']}">
                        <th style="padding:0.5rem 0.6rem;text-align:left;color:{C['muted']};
                                   font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em">Month</th>
                        <th style="padding:0.5rem 0.6rem;text-align:left;color:{C['muted']};
                                   font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em">Total</th>
                        <th style="padding:0.5rem 0.6rem;text-align:left;color:{C['muted']};
                                   font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em">vs Prev Month</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
            """)

# ── Tab 4: Budget vs Actual ───────────────────────────────────────────────────
with tab4:
    month4 = st.selectbox("Month", months, index=months.index(current_month), key="t4_month")
    rows = get_budget_status(month4)

    if not rows:
        st.caption("No budgets set for this month.")
    else:
        labels = [
            f"{r['category_name']} › {r['subcategory_name']}" if r["subcategory_name"] else r["category_name"]
            for r in rows
        ]
        spent_vals     = [r["spent"] for r in rows]
        remaining_vals = [max(r["budget_amount"] - r["spent"], 0) for r in rows]
        spent_colors   = [
            {"ok": C["ok"], "warn": C["warn"], "over": C["over"]}[r["status"]]
            for r in rows
        ]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Spent",
            x=labels, y=spent_vals,
            marker=dict(color=spent_colors, line=dict(width=0)),
            hovertemplate="<b>%{x}</b><br>Spent: &#x20B9;%{y:,.0f}<extra></extra>",
            text=[f"&#x20B9;{v:,.0f}" for v in spent_vals],
            textposition="inside",
            textfont=dict(size=10, color="white"),
            insidetextanchor="middle",
        ))
        fig.add_trace(go.Bar(
            name="Remaining",
            x=labels, y=remaining_vals,
            marker=dict(color=C["border"], line=dict(width=0)),
            hovertemplate="<b>%{x}</b><br>Remaining: &#x20B9;%{y:,.0f}<extra></extra>",
            text=[f"&#x20B9;{v:,.0f}" if v > 0 else "" for v in remaining_vals],
            textposition="inside",
            textfont=dict(size=10, color=C["muted"]),
            insidetextanchor="middle",
        ))
        fig.update_layout(
            **base_layout(),
            barmode="stack",
            xaxis=dict(tickangle=-30, title="", tickfont=dict(size=10)),
            yaxis=dict(
                showgrid=True, gridcolor=C["border"], title="",
                tickprefix="₹", tickformat=",.0f",
            ),
            legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center", bgcolor="rgba(0,0,0,0)"),
            height=360,
        )
        st.plotly_chart(fig, use_container_width=True)

# ── Tab 5: Settlements ────────────────────────────────────────────────────────
with tab5:
    settlements = get_settlements()

    if not settlements:
        st.caption("No settlements recorded yet.")
    else:
        # Summary bar
        total_settled = sum(s["amount"] for s in settlements)
        st.html(f"""
        <div style="background:linear-gradient(135deg,#F0FDF4,#DCFCE7);border-radius:14px;
                    padding:1rem 1.4rem;border-left:4px solid {C['ok']};margin-bottom:1rem;
                    display:flex;justify-content:space-between;align-items:center">
            <div>
                <div style="font-size:0.75rem;color:#15803D;font-weight:600;text-transform:uppercase;
                            letter-spacing:0.06em">Total Settled</div>
                <div style="font-size:1.6rem;font-weight:800;color:#166534">&#x20B9;{total_settled:,.0f}</div>
            </div>
            <div style="text-align:right">
                <div style="font-size:0.75rem;color:#15803D;font-weight:600;text-transform:uppercase;
                            letter-spacing:0.06em">Settlements</div>
                <div style="font-size:1.6rem;font-weight:800;color:#166534">{len(settlements)}</div>
            </div>
        </div>
        """)

        # Settlement trend chart if > 1
        if len(settlements) > 1:
            s_df = pd.DataFrame([
                {"date": s["date"].strftime("%d %b %y") if hasattr(s["date"], "strftime") else str(s["date"]),
                 "amount": s["amount"]}
                for s in reversed(settlements)
            ])
            fig = go.Figure(go.Bar(
                x=s_df["date"], y=s_df["amount"],
                marker=dict(color=C["ok"], line=dict(width=0)),
                text=[f"&#x20B9;{v:,.0f}" for v in s_df["amount"]],
                textposition="outside",
                textfont=dict(size=11),
                hovertemplate="<b>%{x}</b><br>&#x20B9;%{y:,.0f}<extra></extra>",
            ))
            fig.update_layout(
                **base_layout(),
                xaxis=dict(showgrid=False, title=""),
                yaxis=dict(showgrid=True, gridcolor=C["border"], title="",
                           tickprefix="₹", tickformat=",.0f"),
                height=220,
            )
            st.plotly_chart(fig, use_container_width=True)

        # Settlement list
        section_title("History")
        for s in settlements:
            date_str   = s["date"].strftime("%d %b %Y") if hasattr(s["date"], "strftime") else str(s["date"])
            from_badge = person_badge(s["from_person"])
            to_badge   = person_badge(s["to_person"])
            st.html(
                f'<div style="background:{C["card"]};border-radius:12px;'
                f'padding:0.75rem 1rem;border:1px solid {C["border"]};'
                f'margin-bottom:0.5rem;display:flex;align-items:center;gap:0.8rem">'
                f'<div style="width:36px;height:36px;border-radius:99px;background:{C["ok"]}18;'
                f'display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0">&#x1F91D;</div>'
                f'<div style="flex:1">'
                f'<div style="font-size:0.82rem;color:{C["muted"]};margin-bottom:0.2rem">{date_str}</div>'
                f'<div style="font-size:0.88rem">{from_badge} &nbsp;paid&nbsp; {to_badge}</div>'
                f'</div>'
                f'<div style="font-size:1.05rem;font-weight:800;color:{C["ok"]}">&#x20B9;{s["amount"]:,.2f}</div>'
                f'</div>'
            )
