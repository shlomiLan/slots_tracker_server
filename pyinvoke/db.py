import datetime
import os
from itertools import chain

from invoke import task
from progress.bar import Bar

from pyinvoke.base import init_app
from pyinvoke.email import email
from pyinvoke.utils import transform_expense_to_dict, translate, reference_objects_str_to_id, clean_doc_data, BASEDIR, \
    BACKUPS, run, load_yaml_from_file


@task()
def clean_db(c, settings=None):
    init_app(c, settings=settings)
    clean_expenses(c)
    clean_pay_methods(c)
    clean_categories(c)
    clean_kinds(c)
    clean_withdrawals(c)


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

    print('Removing all categories objects')
    Categories.objects.delete()


@task(init_app)
def clean_kinds(_):
    # Leave here tp prevent circular import
    from slots_tracker_server.models import Kinds

    print('Removing all kinds objects')
    Kinds.objects.delete()


@task(init_app)
def clean_withdrawals(_):
    # Leave here tp prevent circular import
    from slots_tracker_server.models import Withdrawal

    print('Removing all withdrawal objects')
    Withdrawal.objects.delete()


@task()
def init_db(c, env=None, settings=None):
    init_app(c, env, settings)
    clean_db(c, settings)
    initial_data = load_yaml_from_file(os.path.join(BASEDIR, 'resources', 'init_db.yml'))
    # Leave here tp prevent circular import
    from slots_tracker_server.models import PayMethods, Categories, Kinds
    insert_db_data(PayMethods, initial_data.get('pay_methods'))
    insert_db_data(Categories, initial_data.get('categories'))
    insert_db_data(Kinds, initial_data.get('kinds'))


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
        res = restore_db(c, today_str)
        if res and res.exited != 0:
            email_text = res.stderr
        else:
            email_text = f'The {today_str} daily backup was restored to stage successfully.'

        email(c, subject='DB restore test', content=email_text)


@task()
def restore_db(c, date, backup_db_name='slots_tracker', settings='stage'):
    init_app(c, settings=settings, force=True)
    host, port, db_name, username, password = get_db_info()
    source_path = os.path.join(BACKUPS, date, backup_db_name)
    if settings == 'dev':
        run(c, f'mongorestore -h {host}:{port} -d {db_name} {source_path} --drop', False)
    else:
        run(c, f'mongorestore -h {host}:{port} -d {db_name} -u {username} -p {password} {source_path} --drop', False)


@task()
def sync_db_from_gsheet(c, settings=None, reset_db=False, cls='expense'):
    init_app(c, settings=settings)
    if reset_db:
        init_db(c, settings=settings)

    import slots_tracker_server.gsheet as gsheet
    from slots_tracker_server.models import Expense, Withdrawal, Kinds

    # Reset only withdrawals data
    # clean_kinds(c)
    clean_withdrawals(c)
    if not Kinds.objects:
        initial_data = load_yaml_from_file(os.path.join(BASEDIR, 'resources', 'init_db.yml'))
        insert_db_data(Kinds, initial_data.get('kinds'))

    cls = Withdrawal if cls != 'expense' else Expense
    wks = gsheet.get_worksheet(cls)
    headers = gsheet.get_headers(wks)
    last_row = gsheet.find_last_row(wks)
    g_data = gsheet.get_all_data(wks)

    # skip the headers row
    for i, row in enumerate(Bar('Reading data').iter(g_data[1:last_row]), start=2):
        doc_data = row[:gsheet.end_column_as_number()]
        # Only write to DB rows without id
        if not doc_data[0]:
            doc_dict = transform_expense_to_dict(doc_data, headers)
            translate(doc_dict)
            reference_objects_str_to_id(doc_dict)
            clean_doc_data(doc_dict)

            doc = cls(**doc_dict).save()
            # Update the id column
            gsheet.update_with_retry(wks, row=i, col=1, value=str(doc.id))


@task()
def add_count_to_ref_fields(c, settings=None):
    init_app(c, settings=settings)
    from slots_tracker_server.models import Expense

    # TODO: Change this so it will make changes based on chain(PayMethods.objects(), Categories.objects()
    # Now we repeat this process to many times
    # expenses = Expense.objects()
    # for expense in Bar('Resting').iter(expenses):
    #     pass
    # expense.update_reference_filed_count(reset=True)

    expenses = Expense.objects()
    for expense in Bar('Updating').iter(expenses):
        expense.update_reference_filed_count()


def get_db_info():
    # Use get to not get error when loading the 'dev' settings
    return os.environ['DB_HOST'], os.environ['DB_PORT'], os.environ['DB_NAME'], os.environ.get('DB_USERNAME'), \
           os.environ.get('DB_PASS')


@task()
def remove_numbers_from_name(c, settings=None):
    init_app(c, settings=settings)

    from slots_tracker_server.models import Categories, PayMethods
    for item in Bar('Updating').iter(chain(PayMethods.objects(), Categories.objects())):
        item_name = item.name
        if item_name[0].isdigit():
            item_name = item_name.split(' ')
            item_name = ' '.join(item_name[1:])
            item.name = item_name
            item.save()
