from slots_tracker_server import app
from slots_tracker_server.expense import ExpenseAPI, PayMethodsAPI
from slots_tracker_server.utils import register_api


@app.route('/')
def home_page():
    return 'Index Page3'


register_api(ExpenseAPI,    'expense_api',     '/expenses/',    pk='obj_id')  # noqa
register_api(PayMethodsAPI, 'pay_methods_api', '/pay_methods/', pk='obj_id')