import connexion
from pymongo import MongoClient

from expense import create_new_expense, expense_data_from_url_parameters


# Create the application instance
app = connexion.App(__name__, specification_dir='./')

# Read the swagger.yml file to configure the endpoints
app.add_api('swagger.yml')

mongo_client = MongoClient()
db = mongo_client['slots_tracker']


@app.route('/')
def home_page():
    return 'Index Page'


@app.route('/expense', methods=['POST'])
def create_expense():
    # TODO: find better way to do that
    amount, desc, pay_method, date = expense_data_from_url_parameters(request.args)
    create_new_expense(mongo_client, amount, desc, pay_method, date)
    return 'Expense Page post'


@app.route('/expense/<int:expense_id>', methods=['GET'])
def read(expense_id):
    expenses_q = mongo_client.expenses.find({'amount': 200})
    return 'Expense Page get'


# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(debug=True)
