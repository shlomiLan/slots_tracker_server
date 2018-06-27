from flask import Flask, render_template, request
from flask_pymongo import PyMongo

from expense import create_new_expense, expense_data_from_url_parameters


app = Flask(__name__)
app.add_api('swagger.yml')
app.config['MONGO_DBNAME'] = 'slots_tracker'
mongo = PyMongo(app)


@app.route('/')
def home_page():
    return 'Index Page'


@app.route('/expense', methods=['POST'])
def create_expense():
    # TODO: find better way to do that
    amount, desc, pay_method, date = expense_data_from_url_parameters(request.args)
    create_new_expense(mongo.db, amount, desc, pay_method, date)
    return 'Expense Page post'


@app.route('/expense/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    expenses_q = mongo.db.expenses.find({'amount': 200})
    return 'Expense Page get'
