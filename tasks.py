from invoke import Collection

from pyinvoke import base, db, email, test, utils, notifications

namespace = Collection(base, db, email, test, utils, notifications)
