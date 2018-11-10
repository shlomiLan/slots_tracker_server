from invoke import Collection

from pyinvoke import base, db, email, gsheet, test, utils, notifications

namespace = Collection(base, db, email, gsheet, test, utils, notifications)
