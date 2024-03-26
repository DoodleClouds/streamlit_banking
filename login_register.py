import pandas as pd
import streamlit as st
import requests

# Set the base URL of your FastAPI backend
base_url = "http://localhost:8082"

# Create a login/register page
def login_register():
    st.subheader("Login/Register")
    menu = ["Login", "Register"]
    choice = st.selectbox("Select an option", menu)

    if choice == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            # Send login request to backend
            login_data = {"username": username, "password": password}
            response = requests.post(f"{base_url}/token", data=login_data)
            if response.status_code == 200:
                access_token = response.json()["access_token"]
                st.success("Logged in successfully!")
                st.session_state.access_token = access_token
                st.experimental_rerun()
            else:
                st.error("Invalid username or password.")

    elif choice == "Register":
        st.subheader("Register")
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Register"):
            user_data = {"username": username, "email": email, "password": password}
            response = requests.post(f"{base_url}/users", json=user_data)
            if response.status_code == 200:
                st.success("User registered successfully!")
            else:
                st.error("Failed to register user.")

# Create account page
def create_account():
    st.subheader("Create Account")
    account_name = st.text_input("Account Name")
    account_type = st.selectbox("Account Type", ['Checkings', 'Savings'])
    balance = st.number_input("Initial Balance")
    if st.button("Create Account"):
        account_data = {
            "user_id": st.session_state.access_token,
            "account_name": account_name,
            "account_type": account_type,
            "balance": balance,
        }
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        response = requests.post(f"{base_url}/accounts", json=account_data, headers=headers)
        if response.status_code == 200:
            st.success("Account created successfully!")
        else:
            st.error("Failed to create account.")