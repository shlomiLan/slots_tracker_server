from invoke import Collection

from pyinvoke import base, db, email, test, utils

namespace = Collection(base, db, email, test, utils)
