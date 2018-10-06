from slots_tracker_server import app, sentry
from slots_tracker_server.apis import ExpenseAPI, PayMethodsAPI, CategoriesAPI
from slots_tracker_server.charts import Charts
from slots_tracker_server.utils import register_api


@app.route('/')
def home_page():
    return 'API index page'


@app.route('/charts/')
def charts():
    chart = Charts()
    return chart.clac_charts()


@app.errorhandler(Exception)
def handle_general_exception(e):
    app.logger.error(e)
    sentry.captureException()
    return "An error occurred, I'm on it to fix it :-)", e.code or 400


register_api(ExpenseAPI, 'expense_api', '/expenses/', pk='obj_id')
register_api(PayMethodsAPI, 'pay_methods_api', '/pay_methods/', pk='obj_id')
register_api(CategoriesAPI, 'categories_api', '/categories/', pk='obj_id')
