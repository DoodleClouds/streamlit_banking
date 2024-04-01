from typing import List
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from datetime import date
import mysql.connector
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI(debug=True)

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="income_expense_tracker"
)

# OAuth2 configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models for request bodies
class User(BaseModel):
    username: str
    email: str
    password: str

class Account(BaseModel):
    user_id: int
    account_name: str
    account_type: str
    balance: float

class Category(BaseModel):
    category_name: str
    category_type: str

class Transaction(BaseModel):
    account_id: int
    category_id: int
    amount: float
    description: str
    transaction_date: date

class TransactionRequest(BaseModel):
    account_ids: List[int]

class Budget(BaseModel):
    user_id: int
    category_id: int
    budget_amount: float
    start_date: date
    end_date: date

class Goal(BaseModel):
    user_id: int
    goal_name: str
    goal_description: str
    target_amount: float
    current_amount: float
    start_date: date
    end_date: date
    is_completed: bool

# Routes

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    cursor = db.cursor()
    query = "SELECT * FROM users WHERE username = %s"
    values = (form_data.username,)
    cursor.execute(query, values)
    user = cursor.fetchone()
    cursor.close()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    if user[3] != form_data.password:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    return {"access_token": user[0], "token_type": "bearer"}

@app.post("/users")
def create_user(user: User):
    cursor = db.cursor()
    query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
    values = (user.username, user.email, user.password)
    cursor.execute(query, values)
    db.commit()
    return {"message": "User created successfully"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    cursor = db.cursor()
    query = "SELECT * FROM users WHERE user_id = %s"
    values = (user_id,)
    cursor.execute(query, values)
    user = cursor.fetchone()
    if user:
        return {"user_id": user[0], "username": user[1], "email": user[2]}
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.post("/accounts")
def create_account(account: Account):
    cursor = db.cursor()
    query = "INSERT INTO accounts (user_id, account_name, account_type, balance) VALUES (%s, %s, %s, %s)"
    values = (account.user_id, account.account_name, account.account_type, account.balance)
    cursor.execute(query, values)
    db.commit()
    return {"message": "Account created successfully"}

@app.get("/accounts")
def get_accounts(token: str = Depends(oauth2_scheme)):
    user_id = int(token)
    cursor = db.cursor()
    query = "SELECT * FROM accounts WHERE user_id = %s"
    values = (user_id,)
    cursor.execute(query, values)
    accounts = cursor.fetchall()
    cursor.close()
    return [{"account_id": account[0], "user_id": account[1], "account_name": account[2], "account_type": account[3], "balance": account[4]} for account in accounts]

@app.get("/accounts/{account_id}")
def get_account(account_id: int):
    cursor = db.cursor()
    query = "SELECT * FROM accounts WHERE account_id = %s"
    values = (account_id,)
    cursor.execute(query, values)
    account = cursor.fetchone()
    if account:
        return {"account_id": account[0], "user_id": account[1], "account_name": account[2], "account_type": account[3], "balance": account[4]}
    else:
        raise HTTPException(status_code=404, detail="Account not found")

@app.get("/categories")
def get_categories():
    cursor = db.cursor()
    query = "SELECT * FROM categories"
    cursor.execute(query)
    categories = cursor.fetchall()
    cursor.close()
    return [{"category_id": category[0], "category_name": category[1], "category_type": category[2]} for category in categories]

@app.post("/categories")
def create_category(category: Category):
    cursor = db.cursor()
    query = "INSERT INTO categories (category_name, category_type) VALUES (%s, %s)"
    values = (category.category_name, category.category_type)
    cursor.execute(query, values)
    db.commit()
    return {"message": "Category created successfully"}

@app.get("/categories/{category_id}")
def get_category(category_id: int):
    cursor = db.cursor()
    query = "SELECT * FROM categories WHERE category_id = %s"
    values = (category_id,)
    cursor.execute(query, values)
    category = cursor.fetchone()
    if category:
        return {"category_id": category[0], "category_name": category[1], "category_type": category[2]}
    else:
        raise HTTPException(status_code=404, detail="Category not found")

@app.post("/transactions")
def create_transaction(transaction: Transaction):
    cursor = db.cursor()
    query = "INSERT INTO transactions (account_id, category_id, amount, description, transaction_date) VALUES (%s, %s, %s, %s, %s)"
    values = (transaction.account_id, transaction.category_id, transaction.amount, transaction.description, transaction.transaction_date)
    cursor.execute(query, values)
    db.commit()
    return {"message": "Transaction created successfully"}

@app.post("/transactions/by_accounts")
def get_transactions_by_accounts(request: TransactionRequest, token: str = Depends(oauth2_scheme)):
    user_id = int(token)
    account_ids = request.account_ids

    cursor = db.cursor()
    query = """
        SELECT t.transaction_id, t.account_id, t.category_id, t.amount, t.description, t.transaction_date
        FROM transactions t
        INNER JOIN accounts a ON t.account_id = a.account_id
        WHERE a.user_id = %s AND t.account_id IN (%s)
    """
    placeholder = ', '.join(['%s'] * len(account_ids))
    query = query % (user_id, placeholder)
    values = account_ids
    cursor.execute(query, values)
    transactions = cursor.fetchall()
    cursor.close()

    return [{"transaction_id": transaction[0], "account_id": transaction[1], "category_id": transaction[2],
             "amount": transaction[3], "description": transaction[4], "transaction_date": transaction[5]}
            for transaction in transactions]


@app.get("/transactions/{transaction_id}")
def get_transaction(transaction_id: int):
    cursor = db.cursor()
    query = "SELECT * FROM transactions WHERE transaction_id = %s"
    values = (transaction_id,)
    cursor.execute(query, values)
    transaction = cursor.fetchone()
    if transaction:
        return {"transaction_id": transaction[0], "account_id": transaction[1], "category_id": transaction[2], "amount": transaction[3], "description": transaction[4], "transaction_date": transaction[5]}
    else:
        raise HTTPException(status_code=404, detail="Transaction not found")

@app.post("/budgets")
def create_budget(budget: Budget):
    cursor = db.cursor()
    query = "INSERT INTO budgets (user_id, category_id, budget_amount, start_date, end_date) VALUES (%s, %s, %s, %s, %s)"
    values = (budget.user_id, budget.category_id, budget.budget_amount, budget.start_date, budget.end_date)
    cursor.execute(query, values)
    db.commit()
    return {"message": "Budget created successfully"}

@app.get("/budgets/{budget_id}")
def get_budget(budget_id: int):
    cursor = db.cursor()
    query = "SELECT * FROM budgets WHERE budget_id = %s"
    values = (budget_id,)
    cursor.execute(query, values)
    budget = cursor.fetchone()
    if budget:
        return {"budget_id": budget[0], "user_id": budget[1], "category_id": budget[2], "budget_amount": budget[3], "start_date": budget[4], "end_date": budget[5]}
    else:
        raise HTTPException(status_code=404, detail="Budget not found")

@app.post("/goals")
def create_goal(goal: Goal):
    cursor = db.cursor()
    query = "INSERT INTO goals (user_id, goal_name, goal_description, target_amount, current_amount, start_date, end_date, is_completed) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    values = (goal.user_id, goal.goal_name, goal.goal_description, goal.target_amount, goal.current_amount, goal.start_date, goal.end_date, goal.is_completed)
    cursor.execute(query, values)
    db.commit()
    return {"message": "Goal created successfully"}

@app.get("/goals")
def get_goals(token: str = Depends(oauth2_scheme)):
    user_id = int(token)

    cursor = db.cursor()
    query = "SELECT * FROM goals WHERE user_id = %s"
    values = (user_id,)
    cursor.execute(query, values)
    goals = cursor.fetchall()
    cursor.close()

    return [{"goal_id": goal[0], "user_id": goal[1], "goal_name": goal[2], "goal_description": goal[3],
             "target_amount": goal[4], "current_amount": goal[5], "start_date": goal[6],
             "end_date": goal[7], "is_completed": goal[8]} for goal in goals]

@app.get("/goals/{goal_id}")
def get_goal(goal_id: int):
    cursor = db.cursor()
    query = "SELECT * FROM goals WHERE goal_id = %s"
    values = (goal_id,)
    cursor.execute(query, values)
    goal = cursor.fetchone()
    if goal:
        return {"goal_id": goal[0], "user_id": goal[1], "goal_name": goal[2], "goal_description": goal[3], "target_amount": goal[4], "current_amount": goal[5], "start_date": goal[6], "end_date": goal[7], "is_completed": goal[8]}
    else:
        raise HTTPException(status_code=404, detail="Goal not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8082)