import streamlit as st
from seed import run as seed_run

st.set_page_config(page_title="Budget Tracker", page_icon="💰", layout="centered")

from components.styles import apply_global_styles, C
apply_global_styles()

if "seeded" not in st.session_state:
    seed_run()
    st.session_state.seeded = True

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown(f"""
    <div style="text-align:center;padding:3rem 1rem 1.5rem">
        <div style="font-size:3.5rem">💰</div>
        <div style="font-size:2rem;font-weight:800;color:{C['text']};margin-top:0.5rem">
            Budget Tracker
        </div>
        <div style="font-size:0.95rem;color:{C['muted']};margin-top:0.3rem">
            Yash & Daksha
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        password = st.text_input("Password", type="password", placeholder="Enter password")
        if st.button("Login", type="primary", use_container_width=True):
            if password == st.secrets.get("APP_PASSWORD", ""):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password")
    st.stop()

st.switch_page("pages/1_Dashboard.py")
