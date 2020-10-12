import os

import requests
from invoke import task
from pyinvoke.utils import load_yaml_from_file, set_env_var, BASEDIR, run


@task()
def init_app(c, env=None, settings=None, force=False):
    # Prevent execute this function more than once
    if force or not os.environ.get('FLASK_APP'):
        # Load the basic configs
        env_vars = load_yaml_from_file(os.path.join(BASEDIR, 'resources', 'settings.yml'))

        if settings and settings != 'dev':
            env_vars.update(load_yaml_from_file(os.path.join(BASEDIR, 'resources', f'settings_{settings}.yml')))

        heroku_app_name = env_vars.pop('HEROKU_APP_NAME').get('value')
        for name, data in env_vars.items():
            set_env_var(c, name, data.get('value'), env, data.get('is_protected', False), heroku_app_name)


@task(init_app)
def run_app(c):
    run(c, 'flask run')


@task(init_app)
def run_app_gunicorn(c):
    run(c, 'gunicorn slots_tracker_server:app')


@task()
def update_requirements(c):
    run(c, 'pip install -r development.txt')


# Heroku
@task(init_app)
def heroku_run(c):
    run(c, 'heroku local', False)


# Scripts (flask scripts)
@task(init_app)
def run_command(c, command):
    run(c, 'cd {} && flask {}'.format(BASEDIR, command))


# jupyter notebook
@task(init_app)
def run_notebook(c):
    run(c, 'jupyter notebook')


# Charts
@task(init_app)
def calc_chart_data_task(_):
    from slots_tracker_server.charts import Charts
    charts = Charts().clac_charts()
    print(charts)
    return charts


# Keep alive - prevent Heroku sleep
@task(init_app)
def keep_server_alive(_):
    from pyinvoke.email import email
    subject = 'Keep server alive error'
    try:
        urls = ['https://slots-tracker.herokuapp.com/', 'https://slots-tracker-client.herokuapp.com/expenses']
        for url in urls:
            res = requests.get(url)
            if res.status_code != 200:
                email(_, subject=subject, content=str(res.__dict__))
    except Exception as e:
        email(_, subject=subject, content=e)


@task(init_app)
def read_expenses_from_files(c, settings='dev'):
    init_app(c, settings=settings, force=True)
    from slots_tracker_server.parser import get_parser_from_file_path

    total_new_expenses, total_new_categories = 0, 0
    for dirpath, _, filenames in os.walk(os.path.join(BASEDIR, 'reports')):
        if filenames:
            for filename in filenames:
                #  TODO: save to var
                if '.DS_Store' in filename:
                    continue

                filepath = os.path.join(dirpath, filename)
                print(f'Working on file: {filepath}')
                parser = get_parser_from_file_path(filepath)
                if parser:
                    new_expenses, new_categories = parser.parse_file()
                    total_new_expenses += len(new_expenses)
                    total_new_categories += len(new_categories)

    print(f'Total number of new expenses: {total_new_expenses}')
    print(f'Total number of new categories: {total_new_categories}')
    from slots_tracker_server.views import monthly_update
    monthly_update()
