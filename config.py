class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'this-really-needs-to-be-changed'
    MONGODB_SETTINGS = dict(db='slots_tracker')
    GSHEET_ID = '1iMG12iT6m_wAyxJoxhXg0zPc8PCRa39J4zMSPKLoulM'


class ProductionConfig(Config):
    DEBUG = False
    MONGODB_SETTINGS = dict(
        host='mongodb://ds145921.mlab.com/slots_tracker', port=45921, username='slots_tracker', password='Q77GdN2^S$0r')


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    MONGODB_SETTINGS = dict(
        host='mongodb://ds145921.mlab.com/slots_tracker', port=45921, username='slots_tracker', password='Q77GdN2^S$0r')


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    MONGODB_SETTINGS = dict(db='slots_tracker_test')
