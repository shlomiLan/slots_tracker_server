from invoke import Collection

from pyinvoke import base, db, email, gsheet, test, utils

namespace = Collection(base, db, email, gsheet, test, utils)
