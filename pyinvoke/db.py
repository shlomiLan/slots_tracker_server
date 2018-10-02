import datetime
import os

from invoke import task

from pyinvoke.base import init_app
from pyinvoke.email import email
from pyinvoke.utils import transform_expense_to_dict, translate, reference_objects_str_to_id, clean_expense, BASEDIR, \
    BACKUPS, run, load_yaml_from_file


@task()
def clean_db(c, settings=None):
    init_app(c, settings=settings)
    clean_expenses(c)
    clean_pay_methods(c)
    clean_categories(c)


@task(init_app)
def clean_expenses(_):
    # Leave here tp prevent circular import
    from slots_tracker_server.models import Expense

    print('Removing all expense objects')
    Expense.objects.delete()


@task(init_app)
def clean_pay_methods(_):
    # Leave here tp prevent circular import
    from slots_tracker_server.models import PayMethods

    print('Removing all pay methods objects')
    PayMethods.objects.delete()


@task(init_app)
def clean_categories(_):
    # Leave here tp prevent circular import
    from slots_tracker_server.models import Categories

    print('Removing all pay methods objects')
    Categories.objects.delete()


@task()
def init_db(c, env=None, settings=None):
    init_app(c, env, settings)
    clean_db(c, settings)
    initial_data = load_yaml_from_file(os.path.join(BASEDIR, 'resources', 'init_db.yml'))
    # Leave here tp prevent circular import
    from slots_tracker_server.models import PayMethods, Categories
    insert_db_data(PayMethods, initial_data.get('pay_methods'))
    insert_db_data(Categories, initial_data.get('categories'))


def insert_db_data(cls, db_data):
    print('Creating {}'.format(cls.__name__))

    for item in db_data:
        cls(name=item).save()


@task()
def backup_db(c, settings='prod', force_restore=False):
    init_app(c, settings=settings)
    host, port, db_name, username, password = get_db_info()
    today_str = str(datetime.datetime.now().date()).replace('-', '_')
    dest_path = os.path.join(BACKUPS, today_str)
    run(c, f'mongodump -h {host}:{port} -d {db_name} -u {username} -p {password} -o {dest_path}', False)

    day = datetime.datetime.now().day
    # If first backup of the month or force
    if day <= 7 or force_restore:
        restore_db(c, today_str)
        email(c, subject='DB restore test', content=f'The {today_str} daily backup was restored to stage successfully.')


@task()
def restore_db(c, date, backup_db_name='slots_tracker', settings='stage'):
    init_app(c, settings=settings)
    host, port, db_name, username, password = get_db_info()
    source_path = os.path.join(BACKUPS, date, backup_db_name)
    run(c, f'mongorestore -h {host}:{port} -d {db_name} -u {username} -p {password} {source_path} --drop', False)


@task()
def sync_db_from_gsheet(c, settings=None, reset_db=True):
    init_app(c, settings=settings)
    if reset_db:
        init_db(c, settings=settings)

    import slots_tracker_server.gsheet as gsheet
    wks = gsheet.get_worksheet()
    headers = gsheet.get_headers(wks)
    last_row = gsheet.find_last_row(wks)
    g_data = gsheet.get_all_data(wks)

    # skip the headers row
    for i, row in enumerate(g_data[1:last_row], start=2):
        expense_data = row[:gsheet.end_column_as_number()]
        # Only write to DB rows without id
        if not expense_data[0]:
            print(f'Processing row number: {i}')
            expense_dict = transform_expense_to_dict(expense_data, headers)
            translate(expense_dict)
            reference_objects_str_to_id(expense_dict)
            clean_expense(expense_dict)

            from slots_tracker_server.models import Expense
            expense = Expense(**expense_dict).save()
            # Update the id column
            gsheet.update_with_retry(wks, row=i, col=1, value=str(expense.id))


@task(init_app)
def add_count_to_ref_fields(_):
    from slots_tracker_server.models import Expense, Categories

    expenses = Expense.objects()
    for expense in expenses:
        category = expense.category
        expense.update_reference_filed_count(reset=True)
        _ = Categories.objects().get(id=category.id)

    expenses = Expense.objects()
    for expense in expenses:
        category = expense.category
        expense.update_reference_filed_count()
        _ = Categories.objects().get(id=category.id)


def get_db_info():
    return os.environ['DB_HOST'], os.environ['DB_PORT'], os.environ['DB_NAME'], os.environ['DB_USERNAME'], \
           os.environ['DB_PASS']
