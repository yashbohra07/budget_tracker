import os
from dotenv import load_dotenv

load_dotenv()

def _get(key: str) -> str:
    """Try os.environ first (local .env), fall back to st.secrets (Streamlit Cloud)."""
    val = os.environ.get(key)
    if val:
        return val
    try:
        import streamlit as st
        return st.secrets[key]
    except Exception:
        raise KeyError(f"Missing required config key: '{key}'. Set it in .env or Streamlit secrets.")

PERSONS = ["Yash", "Daksha"]

DEFAULT_CATEGORIES = [
    {
        "name": "Household",
        "subcategories": [
            {"name": "Rent",        "assignee": "Yash"},
            {"name": "Grocery",     "assignee": "Daksha"},
            {"name": "House Help",  "assignee": "Daksha"},
            {"name": "Electricity", "assignee": "Yash"},
            {"name": "Water",       "assignee": "Yash"},
            {"name": "Internet",    "assignee": "Yash"},
            {"name": "Gas",         "assignee": None},
        ],
    },
    {
        "name": "Transportation",
        "subcategories": [
            {"name": "Bike Fuel - Yash",   "assignee": "Yash"},
            {"name": "Bike Fuel - Daksha", "assignee": "Daksha"},
            {"name": "Metro / Bus",        "assignee": None},
            {"name": "Cab",                "assignee": None},
            {"name": "Flight",             "assignee": None},
            {"name": "Servicing",          "assignee": None},
        ],
    },
    {
        "name": "Food",
        "subcategories": [
            {"name": "Dining Out",     "assignee": None},
            {"name": "Food Delivery",  "assignee": None},
            {"name": "Snacks",         "assignee": None},
        ],
    },
    {
        "name": "Health",
        "subcategories": [
            {"name": "Medicine",  "assignee": None},
            {"name": "Doctor",    "assignee": None},
            {"name": "Gym",       "assignee": "Yash"},
            {"name": "Yoga",      "assignee": "Daksha"},
        ],
    },
    {
        "name": "Personal Care",
        "subcategories": [
            {"name": "Haircut / Salon", "assignee": None},
            {"name": "Clothing",        "assignee": None},
        ],
    },
    {
        "name": "Entertainment",
        "subcategories": [
            {"name": "OTT / Subscriptions", "assignee": "Yash"},
            {"name": "Movies",              "assignee": None},
            {"name": "Events",              "assignee": None},
        ],
    },
    {
        "name": "Savings & Investment",
        "subcategories": [
            {"name": "SIP",            "assignee": None},
            {"name": "Emergency Fund", "assignee": None},
        ],
    },
    {
        "name": "Miscellaneous",
        "subcategories": [
            {"name": "Other", "assignee": None},
        ],
    },
]
