import unittest
import sys
import os

# Add project root to sys.path to allow app import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, expenses as app_expenses, next_expense_id as app_next_expense_id # Import app and global stores

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for testing forms if applicable

        # Reset global in-memory store before each test
        # Access and modify the global variables from the imported app module
        app_expenses[:] = []
        # To modify a global variable from another module, you need to rebind it in that module
        # or have a function in that module to reset it.
        # For simplicity, we'll directly modify if Python's import system allows (which it does for lists)
        # For immutable types like 'int', direct reassignment won't work as expected across modules
        # without a reset function in app.py or by directly setting app.next_expense_id if it were an attribute of app

        # Resetting next_expense_id requires a bit more care if it's just a global int in app.py
        # A common pattern is to have a reset function in app.py or to re-import/re-initialize app logic
        # For now, we'll assume direct manipulation or we'll add a resetter if needed.
        # Let's try to reset it by re-assigning the imported name.
        # This won't actually change next_expense_id in app.py, only our local tests/test_app.py copy.
        # This means tests relying on next_expense_id starting at 1 after the first test might fail
        # or behave unexpectedly.
        # The correct way is:
        # In app.py:
        # def reset_globals():
        #   global next_expense_id, expenses
        #   expenses = []
        #   next_expense_id = 1
        # Then call app.reset_globals() here.
        # For now, we'll proceed and address if it becomes an issue.
# globals()['app_next_expense_id'] = 1 # This is tricky, see above.
        # A better way for next_expense_id, if we can't modify app.py for a reset function:
        import app as main_app_module
        main_app_module.next_expense_id = 1


    def tearDown(self):
        # Clean up (if any) after each test
        # For example, pop the application context
        self.app_context.pop()
        # pass # Not needed

    def test_home_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Assuming "Expense Tracker" is in the title or a prominent heading from base.html
        self.assertIn(b"Expense Tracker", response.data)
        self.assertIn(b"Home - Expense Tracker", response.data) # From title block

    def test_add_expense_get_page_loads(self):
        response = self.client.get('/add')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Add New Expense", response.data)

    def test_add_expense_post(self):
        initial_expense_count = len(app_expenses)
        # Ensure next_expense_id is what we expect before adding
        current_next_id = main_app_module.next_expense_id

        response = self.client.post('/add', data={
            'description': 'Test Coffee', 'amount': '2.50', 'category': 'Food', 'date': '2023-10-27'
        }, follow_redirects=False) # Test redirect first

        self.assertEqual(response.status_code, 302) # Should redirect to home
        self.assertEqual(response.location, '/') # Check redirect location

        # Verify the state after redirect (or by getting the page again)
        self.assertEqual(len(app_expenses), initial_expense_count + 1)
        self.assertEqual(app_expenses[-1]['description'], 'Test Coffee')
        self.assertEqual(app_expenses[-1]['amount'], 2.50)
        self.assertEqual(app_expenses[-1]['category'], 'Food')
        self.assertEqual(app_expenses[-1]['date'], '2023-10-27')
        self.assertEqual(app_expenses[-1]['id'], current_next_id)
        self.assertEqual(main_app_module.next_expense_id, current_next_id + 1)

    def test_add_expense_post_invalid_amount(self):
        initial_expense_count = len(app_expenses)
        response = self.client.post('/add', data={
            'description': 'Invalid Test', 'amount': '-5.00', 'category': 'Error', 'date': '2023-10-27'
        })
        self.assertEqual(response.status_code, 200) # Re-renders the form
        self.assertIn(b"Amount must be a positive number.", response.data)
        self.assertEqual(len(app_expenses), initial_expense_count) # No expense should be added

    def test_view_expenses_empty(self):
        # expenses is already empty due to setUp
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No expenses recorded yet.", response.data)

    def test_view_expenses_with_data(self):
        # Add sample expenses
        app_expenses.append({'id': 1, 'description': 'Lunch', 'amount': 15.00, 'category': 'Food', 'date': '2023-10-26'})
        app_expenses.append({'id': 2, 'description': 'Movie Ticket', 'amount': 12.50, 'category': 'Entertainment', 'date': '2023-10-25'})
        main_app_module.next_expense_id = 3 # Manually update if not done by an add call

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Lunch", response.data)
        self.assertIn(b"$15.00", response.data) # Check formatted amount
        self.assertIn(b"Movie Ticket", response.data)
        self.assertIn(b"$12.50", response.data)
        self.assertNotIn(b"No expenses recorded yet.", response.data)

    def test_edit_expense_get_post(self):
        # 1. Add a sample expense
        app_expenses.append({'id': 1, 'description': 'Original Book', 'amount': 20.00, 'category': 'Education', 'date': '2023-10-01'})
        main_app_module.next_expense_id = 2

        # 2. Test GET request for edit page
        response_get = self.client.get('/edit/1')
        self.assertEqual(response_get.status_code, 200)
        self.assertIn(b"Edit Expense", response_get.data)
        self.assertIn(b'value="Original Book"', response_get.data)
        self.assertIn(b'value="20.0"', response_get.data) # Floats might be tricky with exact match
        self.assertIn(b'value="Education"', response_get.data)
        self.assertIn(b'value="2023-10-01"', response_get.data)

        # 3. Test POST request to update the expense
        updated_data = {
            'description': 'Updated SciFi Book', 'amount': '22.50', 'category': 'Books', 'date': '2023-10-02'
        }
        response_post = self.client.post('/edit/1', data=updated_data, follow_redirects=False)
        self.assertEqual(response_post.status_code, 302)
        self.assertEqual(response_post.location, '/')

        # 4. Verify the expense was updated
        self.assertEqual(len(app_expenses), 1)
        updated_expense = app_expenses[0]
        self.assertEqual(updated_expense['description'], 'Updated SciFi Book')
        self.assertEqual(updated_expense['amount'], 22.50)
        self.assertEqual(updated_expense['category'], 'Books')
        self.assertEqual(updated_expense['date'], '2023-10-02')

    def test_edit_expense_post_invalid_amount(self):
        app_expenses.append({'id': 1, 'description': 'Test Item', 'amount': 10.00, 'category': 'Test', 'date': '2023-01-01'})
        main_app_module.next_expense_id = 2

        response = self.client.post('/edit/1', data={
            'description': 'Updated Item', 'amount': '-5.00', 'category': 'Test', 'date': '2023-01-01'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Amount must be a positive number.", response.data)
        # Check that original data is still there
        self.assertEqual(app_expenses[0]['amount'], 10.00)


    def test_edit_non_existent_expense(self):
        response_get = self.client.get('/edit/999')
        self.assertEqual(response_get.status_code, 404)

        response_post = self.client.post('/edit/999', data={
            'description': 'Ghost', 'amount': '10', 'category': 'None', 'date': '2023-01-01'
        })
        self.assertEqual(response_post.status_code, 404)

    def test_delete_expense(self):
        app_expenses.append({'id': 1, 'description': 'To Delete', 'amount': 5.00, 'category': 'Misc', 'date': '2023-10-03'})
        main_app_module.next_expense_id = 2
        initial_count = len(app_expenses)

        response = self.client.post('/delete/1', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/')
        self.assertEqual(len(app_expenses), initial_count - 1)
        self.assertTrue(all(e['id'] != 1 for e in app_expenses))

    def test_delete_non_existent_expense(self):
        response = self.client.post('/delete/999')
        self.assertEqual(response.status_code, 404)

    def test_summary_page(self):
        app_expenses.append({'id': 1, 'description': 'Item 1', 'amount': 10.00, 'category': 'A', 'date': '2023-01-01'})
        app_expenses.append({'id': 2, 'description': 'Item 2', 'amount': 20.50, 'category': 'B', 'date': '2023-01-02'})
        app_expenses.append({'id': 3, 'description': 'Item 3', 'amount': 0.50, 'category': 'C', 'date': '2023-01-03'})
        main_app_module.next_expense_id = 4

        response = self.client.get('/summary')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Expense Summary", response.data)
        # Total: 10.00 + 20.50 + 0.50 = 31.00
        self.assertIn(b"$31.00", response.data) # Check for formatted total

    def test_summary_page_empty(self):
        response = self.client.get('/summary')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Expense Summary", response.data)
        self.assertIn(b"$0.00", response.data)

if __name__ == '__main__':
    unittest.main()
