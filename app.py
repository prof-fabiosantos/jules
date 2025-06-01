from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

expenses = []
next_expense_id = 1

@app.route('/')
def hello_world():
    return render_template('index.html', expenses=expenses)

def get_expense_by_id(expense_id):
    for expense in expenses:
        if expense['id'] == expense_id:
            return expense
    return None

@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    global next_expense_id
    if request.method == 'POST':
        description = request.form['description']
        amount_str = request.form['amount']
        category = request.form['category']
        date = request.form['date']

        if not amount_str or float(amount_str) <= 0:
            return render_template('add_expense.html', error_message="Amount must be a positive number.")

        amount = float(amount_str)

        expense = {
            'id': next_expense_id,
            'description': description,
            'amount': amount,
            'category': category,
            'date': date
        }
        expenses.append(expense)
        next_expense_id += 1
        return redirect(url_for('hello_world'))
    return render_template('add_expense.html')

@app.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    expense = get_expense_by_id(expense_id)
    if not expense:
        return "Expense not found", 404 # Or redirect with error

    if request.method == 'POST':
        description = request.form['description']
        amount_str = request.form['amount']
        category = request.form['category']
        date = request.form['date']

        if not amount_str or float(amount_str) <= 0:
            return render_template('edit_expense.html', expense=expense, error_message="Amount must be a positive number.")

        amount = float(amount_str)

        expense['description'] = description
        expense['amount'] = amount
        expense['category'] = category
        expense['date'] = date
        return redirect(url_for('hello_world'))

    return render_template('edit_expense.html', expense=expense)

@app.route('/delete/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    global expenses
    expense = get_expense_by_id(expense_id)
    if not expense:
        return "Expense not found", 404 # Or redirect with error
    expenses = [e for e in expenses if e['id'] != expense_id]
    return redirect(url_for('hello_world'))

@app.route('/summary')
def summary():
    total_expenses = sum(expense['amount'] for expense in expenses)
    return render_template('summary.html', total_expenses=total_expenses)

if __name__ == '__main__':
    app.run(debug=True)
