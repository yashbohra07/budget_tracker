import streamlit as st
from pymongo import MongoClient
from config import _get


@st.cache_resource
def get_client():
    return MongoClient(_get("MONGO_URI"))


def get_db():
    return get_client()[_get("DB_NAME")]
