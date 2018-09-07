from slots_tracker_server import app
from slots_tracker_server.apis import ExpenseAPI, PayMethodsAPI, CategoriesAPI
from slots_tracker_server.utils import register_api


@app.route('/')
def home_page():
    return 'API index page'


register_api(ExpenseAPI, 'expense_api', '/expenses/', pk='obj_id')
register_api(PayMethodsAPI, 'pay_methods_api', '/pay_methods/', pk='obj_id')
register_api(CategoriesAPI, 'categories_api', '/categories/', pk='obj_id')
