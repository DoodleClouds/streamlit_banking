import pandas as pd
import streamlit as st
import requests
from login_register import login_register
from main_app import main_app

# Set the base URL of your FastAPI backend
base_url = "http://localhost:8082"

# Set page title and header
st.set_page_config(page_title="Income/Expense Tracker", page_icon=":money_with_wings:")
st.title("Income/Expense Tracker")

# Check if the user is logged in
if "access_token" not in st.session_state:
    login_register()
else:
    main_app()