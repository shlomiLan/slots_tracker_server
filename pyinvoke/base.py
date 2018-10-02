import os

from invoke import task

from pyinvoke.utils import load_yaml_from_file, set_env_var, BASEDIR, run


@task()
def init_app(c, env=None, settings=None):
    # Prevent execute this function more than once
    if not os.environ.get('APP_SETTINGS'):
        # Load the basic configs
        env_vars = load_yaml_from_file(os.path.join(BASEDIR, 'resources', 'settings.yml'))

        if settings:
            env_vars.update(load_yaml_from_file(os.path.join(BASEDIR, 'resources', f'settings_{settings}.yml')))

        heroku_app_name = env_vars.pop('HEROKU_APP_NAME').get('value')
        for name, data in env_vars.items():
            set_env_var(c, name, data.get('value'), env, data.get('is_protected', False), heroku_app_name)


@task(init_app)
def run_app(c):
    run(c, 'flask run')


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
