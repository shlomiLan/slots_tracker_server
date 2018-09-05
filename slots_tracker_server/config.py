import os
from typing import Dict, Any


class Config(object):
    DEBUG = False
    TESTING = False
    MONGODB_SETTINGS: Dict[str, Any] = dict(db='slots_tracker')
    GSHEET_ID = '1iMG12iT6m_wAyxJoxhXg0zPc8PCRa39J4zMSPKLoulM'


class ProductionConfig(Config):
    MONGODB_SETTINGS = dict(host=os.environ['DB_HOST'], port=int(os.environ['DB_PORT']), name=os.environ['DB_NAME'],
                            username=os.environ['DB_USERNAME'], password=os.environ['DB_PASS'])


class StagingConfig(ProductionConfig):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    MONGODB_SETTINGS = dict(db='slots_tracker_test')
