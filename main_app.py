import pandas as pd
import streamlit as st
import requests
from login_register import create_account

# Set the base URL of your FastAPI backend
base_url = "http://localhost:8082"

# Create the main app
def main_app():
    function_menu = ['--','Bank Account', 'Transaction', 'Goal']
    function = st.sidebar.selectbox("Select an option", function_menu)
    choice = '--'
    if function == "Bank Account":
        st.sidebar.title("Bank Account")
        # Account Menu
        account_menu = ['--', "Create Account", "Update Account", "Delete Account"]
        choice = st.sidebar.selectbox("Select an option", account_menu)

    if function == 'Transaction':
        st.sidebar.title("Transaction")
        # Create a sidebar menu
        transaction_menu = ['--', "Add Transaction", "View Transactions"]
        choice = st.sidebar.selectbox("Select an option", transaction_menu)

    if function == 'Goal':
        st.sidebar.title("Goal")
        # Create a sidebar menu
        goal_menu = ['--', "Add Goal", "View Goals"]
        choice = st.sidebar.selectbox("Select an option", goal_menu)

    if choice == '--':
        st.write(f"Welcome to your Dashboard")
        st.header("Accounts")
        # Check if the user has an account
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        response = requests.get(f"{base_url}/accounts", headers=headers)
        accounts = response.json()
        private_info = ['account_id', 'user_id']
        data = [[accounts[i][key] for key in accounts[i] if key not in private_info] for i in range(len(accounts))]
        accounts_df = pd.DataFrame(data, columns=['Account Name', "Account Type", "Balance"])
        st.dataframe(accounts_df, use_container_width=True, hide_index=True)
        col1, col2 = st.columns([3, 1])
        with col1:
            st.header("Transactions")
            transaction_request = {"account_ids": [accounts[i]['account_id'] for i in range(len(accounts))]}
            account_ids = [accounts[i]['account_id'] for i in range(len(accounts))]
            account_names = [accounts[i]['account_name'] for i in range(len(accounts))]
            account_dict = dict(zip(account_ids, account_names))
            headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
            response = requests.post(f"{base_url}/transactions/by_accounts", json=transaction_request, headers=headers)
            transactions = response.json()

            if len(transactions) > 0:
                # Fetch categories
                response = requests.get(f"{base_url}/categories", headers=headers)
                categories = response.json()
                category_map = {category["category_id"]: category["category_name"] for category in categories}

                # Prepare data for the table
                table_data = []
                for transaction in transactions:
                    category_name = category_map.get(transaction["category_id"], "Unknown")
                    table_data.append([
                        transaction["transaction_id"],
                        account_dict[transaction["account_id"]],
                        category_name,
                        transaction["amount"],
                        transaction["description"],
                        transaction["transaction_date"]
                    ])

                # Display the table
                df = pd.DataFrame(
                    table_data,
                    columns=["Transaction ID", "Account Name", "Category", "Amount", "Description", "Date"]
                )
                st.dataframe(df[["Account Name", "Category", "Amount", "Description", "Date"]], hide_index=True,
                             use_container_width=True)
            else:
                st.warning("No transactions found for the selected accounts.")

        with col2:
            st.header("Filter")
            st.write("Blep")

        if st.button("Logout"):
            # Delete all the items in Session state
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()
    # Create Account
    if choice == "Create Account":
        create_account()

    # Check if the user has an account
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    response = requests.get(f"{base_url}/accounts", headers=headers)
    accounts = response.json()

    # Add Transaction
    if choice == "Add Transaction" and len(accounts) > 0:
        st.subheader("Add Transaction")
        selected_account = st.selectbox("Select Account", [account["account_name"] for account in accounts])
        account_id = next(account["account_id"] for account in accounts if account["account_name"] == selected_account)

        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        response = requests.get(f"{base_url}/categories", headers=headers)
        categories = response.json()
        category_type_names = list(set([category["category_type"] for category in categories]))
        selected_category_type = st.selectbox("Select Category Type", category_type_names)


        category_names = list(set([category["category_name"] for category in categories if category['category_type'] == selected_category_type]))
        selected_category = st.selectbox("Select Category", category_names)
        category_id = next(
            category["category_id"] for category in categories if category["category_name"] == selected_category)
        category_type = next(
            category["category_type"] for category in categories if category["category_name"] == selected_category)

        amount = st.number_input("Amount")
        description = st.text_input("Description")
        transaction_date = st.date_input("Transaction Date")

        if st.button("Add Transaction"):
            transaction_data = {
                "account_id": account_id,
                "category_id": category_id,
                "amount": amount if category_type == "income" else -amount,
                "description": description,
                "transaction_date": transaction_date.strftime("%Y-%m-%d"),
            }
            response = requests.post(f"{base_url}/transactions", json=transaction_data, headers=headers)
            if response.status_code == 200:
                st.success("Transaction added successfully!")
            else:
                st.error("Failed to add transaction.")
    elif choice == "Add Transaction" and len(accounts) == 0:
        st.warning("Please create an account first.")

    # View Transactions
    if choice == "View Transactions" and len(accounts) > 0:
        st.subheader("View Transactions")
        selected_accounts = st.multiselect("Select Accounts", [account["account_name"] for account in accounts])
        selected_account_ids = [account["account_id"] for account in accounts if
                                account["account_name"] in selected_accounts]

        if st.button("View Transactions"):
            transaction_request = {"account_ids": selected_account_ids}
            headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
            response = requests.post(f"{base_url}/transactions/by_accounts", json=transaction_request, headers=headers)
            transactions = response.json()

            if len(transactions) > 0:
                # Fetch categories
                response = requests.get(f"{base_url}/categories", headers=headers)
                categories = response.json()
                category_map = {category["category_id"]: category["category_name"] for category in categories}

                # Prepare data for the table
                table_data = []
                for transaction in transactions:
                    category_name = category_map.get(transaction["category_id"], "Unknown")
                    table_data.append([
                        transaction["transaction_id"],
                        transaction["account_id"],
                        category_name,
                        transaction["amount"],
                        transaction["description"],
                        transaction["transaction_date"]
                    ])

                # Display the table
                df = pd.DataFrame(
                    table_data,
                    columns=["Transaction ID", "Account ID", "Category", "Amount", "Description", "Date"]
                )
                st.dataframe(df[["Category", "Amount", "Description", "Date"]], hide_index=True, use_container_width=True)
            else:
                st.warning("No transactions found for the selected accounts.")
    elif choice == "View Transactions" and len(accounts) == 0:
        st.warning("Please create an account first.")


    # Add Goal
    if choice == "Add Goal":
        st.subheader("Add Goal")
        goal_name = st.text_input("Goal Name")
        goal_description = st.text_area("Goal Description")
        target_amount = st.number_input("Target Amount")
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        if st.button("Add Goal"):
            goal_data = {
                "user_id": st.session_state.access_token,
                "goal_name": goal_name,
                "goal_description": goal_description,
                "target_amount": target_amount,
                "current_amount": 0,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "is_completed": False,
            }
            headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
            response = requests.post(f"{base_url}/goals", json=goal_data, headers=headers)
            if response.status_code == 200:
                st.success("Goal added successfully!")
            else:
                st.error("Failed to add goal.")

    # View Goals
    if choice == "View Goals":
        st.subheader("View Goals")
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        response = requests.get(f"{base_url}/goals", headers=headers)
        goals = response.json()

        if len(goals) > 0:
            table_data = []
            for goal in goals:
                table_data.append([
                    goal["goal_name"],
                    goal["goal_description"],
                    goal["target_amount"],
                    goal["current_amount"],
                    goal["start_date"],
                    goal["end_date"],
                    goal["is_completed"]
                ])

            df = pd.DataFrame(
                table_data,
                columns=["Goal Name", "Description", "Target Amount", "Current Amount", "Start Date",
                         "End Date", "Is Completed"]
            )
            st.data_editor(df)
        else:
            st.warning("No goals found.")