import random

from fastmcp import FastMCP
import sqlite3

def create_database():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            subcategory TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
create_database()

mcp= FastMCP()


@mcp.tool()
def add_expense(category: str, subcategory: str, description: str, amount: float, date: str):
    """
Add a new expense to the database with the given details.
category: The main category of the expense (e.g., "Food", "Transportation").
subcategory: The subcategory of the expense (e.g., "Groceries", "Public Transit").
description: A brief description of the expense.
amount: The monetary amount of the expense.
date: The date when the expense was incurred.
    """
    
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO expenses (category, subcategory, description, amount, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (category, subcategory, description, amount, date))
    conn.commit()
    conn.close()

@mcp.tool()
def get_expenses(category: str = None, subcategory: str = None, start_date: str = None, end_date: str = None):
    """
Retrieve expenses from the database based on optional filters.
category: Filter expenses by main category (e.g., "Food").
subcategory: Filter expenses by subcategory (e.g., "Groceries").
start_date: Filter expenses incurred on or after this date (format: "YYYY-MM-DD").
end_date: Filter expenses incurred on or before this date (format: "YYYY-MM-DD").
Returns a list of expenses matching the specified criteria.
    """
    
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    query = 'SELECT * FROM expenses WHERE 1=1'
    params = []

    if category:
        query += ' AND category = ?'
        params.append(category)
    if subcategory:
        query += ' AND subcategory = ?'
        params.append(subcategory)
    if start_date:
        query += ' AND date >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND date <= ?'
        params.append(end_date)

    cursor.execute(query, params)
    expenses = cursor.fetchall()
    conn.close()
    return expenses

@mcp.tool()
def delete_expense(expense_id: int):
    """
    Delete an expense from the database by ID.
    expense_id: The ID of the expense to delete.
    """
    
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    conn.commit()
    conn.close()
    
@mcp.tool()
def update_expense(expense_id: int, category: str = None, subcategory: str = None, description: str = None, amount: float = None, date: str = None):
    """
    Update an existing expense in the database by ID.
    expense_id: The ID of the expense to update.
    category: The updated main category of the expense.
    subcategory: The updated subcategory of the expense.
    description: The updated description of the expense.
    amount: The updated monetary amount of the expense.
    date: The updated date when the expense was incurred.
    """
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    query = 'UPDATE expenses SET'
    params = []

    if category:
        query += ' category = ?,'
        params.append(category)
    if subcategory:
        query += ' subcategory = ?,'
        params.append(subcategory)
    if description:
        query += ' description = ?,'
        params.append(description)
    if amount is not None:
        query += ' amount = ?,'
        params.append(amount)
    if date:
        query += ' date = ?,'
        params.append(date)

    # Remove the trailing comma and add the WHERE clause
    query = query.rstrip(',') + ' WHERE id = ?'
    params.append(expense_id)

    cursor.execute(query, params)
    conn.commit()
    conn.close()
    
@mcp.tool()
def get_expense_by_id(expense_id: int):
    """
Retrieve a single expense from the database by its ID.
expense_id: The ID of the expense to retrieve.
Returns the expense details if found, otherwise returns None.
    """
    
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,))
    expense = cursor.fetchone()
    conn.close()
    return expense

@mcp.tool()
def get_expense_summary(start_date: str = None, end_date: str = None):
    """
    Get a summary of expenses by category and subcategory.
    start_date: Filter expenses incurred on or after this date (format: "YYYY-MM-DD").
    end_date: Filter expenses incurred on or before this date (format: "YYYY-MM-DD").
    Returns a list of expense summaries matching the specified criteria.
    """
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    query = '''
        SELECT category, subcategory, SUM(amount) as total_amount
        FROM expenses
        WHERE 1=1
    '''
    params = []

    if start_date:
        query += ' AND date >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND date <= ?'
        params.append(end_date)

    query += ' GROUP BY category, subcategory'

    cursor.execute(query, params)
    summary = cursor.fetchall()
    conn.close()
    return summary




if __name__ == "__main__":
    mcp.run()