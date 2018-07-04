from server import app
from server.expense import ExpenseAPI
from server.utils import register_api


@app.route('/')
def home_page():
    return 'Index Page3'


register_api(ExpenseAPI, 'expense_api', '/expenses/', pk='expense_id')
