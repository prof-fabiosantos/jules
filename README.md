# Personal Expense Tracker

A simple web application built with Python and Flask to track personal expenses.

## Prerequisites

- Python 3.x
- pip (Python package installer)

## Installation

1.  Clone the repository: `git clone https://your-repository-url-here.com/personal-expense-tracker.git`
2.  Navigate to the project directory: `cd personal-expense-tracker`
3.  Install dependencies: `pip install Flask`

## Running the Application

1.  Run the Flask development server: `python app.py`
2.  Open your web browser and go to: `http://127.0.0.1:5000/`

### Running Tests

To run the automated tests, navigate to the project's root directory and execute the following command:

```bash
python -m unittest discover tests
```

This will automatically discover and run all tests within the `tests` directory.

## How to Use

-   **Home Page (`/`):** View all your recorded expenses. You can edit or delete expenses from here.
-   **Add Expense (`/add`):** Fill in the form to add a new expense (description, amount, category, date).
-   **Edit Expense (`/edit/<id>`):** Modify the details of an existing expense.
-   **Delete Expense (`/delete/<id>`):** Remove an expense from your records (a confirmation will be asked).
-   **Summary (`/summary`):** View the total amount of all recorded expenses.
