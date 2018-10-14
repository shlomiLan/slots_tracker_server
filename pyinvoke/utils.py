import json
import os

import yaml
from mongoengine import DoesNotExist

BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))

BACKUPS = os.path.join(BASEDIR, 'backups')


def run(c, command, with_venv=True):
    if with_venv:
        command = '{} && {}'.format(get_venv_action(), command)

    print('Running: {}'.format(command))
    c.run(command)


def set_env_var(c, name, value, env, is_protected=True, heroku_app_name=None):
    # env codes: h - Heroku, t - Travis-CI
    if isinstance(value, dict):
        value = json.dumps(value)

    if env in ['h', 't']:
        command = ''
        if env == 'h':
            command = "heroku config:set {}='{}' -a {}".format(name, value, heroku_app_name)
        elif env == 't':
            command = "travis env set {} '{}'".format(name, value)
            if not is_protected:
                command = '{} --public'.format(command)

        if command:
            run(c, command, False)

    else:
        print(f'Set local var: {name}={value}')
        os.environ[name] = value


def load_yaml_from_file(file_path):
    with open(file_path, 'r') as stream:
        return yaml.safe_load(stream)


def is_unix():
    return os.name == 'posix'


def get_venv_action():
    if is_unix():
        return f'source {BASEDIR}/venv/bin/activate'
    else:
        return f'{BASEDIR}\\venv\\Scripts\\activate'


def translate(doc_data):
    trans_data = load_yaml_from_file(os.path.join(BASEDIR, 'resources', 'translate.yml'))

    for k, v in doc_data.items():
        if trans_data.get(k):
            if trans_data[k].get(v):
                doc_data[k] = trans_data[k][v]


def transform_expense_to_dict(expense_data, headers):
    return {headers[i].value: expense_data[i] for i in range(len(expense_data))}


def reference_objects_str_to_id(doc_data):
    from slots_tracker_server.models import PayMethods, Categories, Kinds
    try:
        doc_data['pay_method'] = PayMethods.objects.get(name=doc_data.get('pay_method'))
    except DoesNotExist:
        print(f'Error in Pay method: {doc_data.get("pay_method")}')

    try:
        if doc_data.get('category'):
            doc_data['category'] = Categories.objects.get(name=doc_data.get('category'))
    except DoesNotExist:
        print(f'Error in Category: {doc_data.get("category")}')
    try:
        if doc_data.get('kind'):
            doc_data['kind'] = Kinds.objects.get(name=doc_data.get('kind'))
    except DoesNotExist:
        print(f'Error in Kind: {doc_data.get("kind")}')


def clean_doc_data(doc_data):
    del doc_data['_id']
    doc_data['amount'] = doc_data.get('amount').replace(',', '')
    if doc_data.get('one_time'):
        doc_data['one_time'] = doc_data['one_time'] == 'one_time'
    if '/' in doc_data['timestamp']:
        day, month, year = doc_data['timestamp'].split('/')
        doc_data['timestamp'] = f'20{year}-{month}-{day}'
