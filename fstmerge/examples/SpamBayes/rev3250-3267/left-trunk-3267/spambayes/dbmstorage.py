"""Wrapper to open an appropriate dbm storage type."""
from spambayes.Options import options
import sys
import whichdb
import os
class error(Exception):
    pass
def open_db3hash(*args):
    """Open a bsddb3 hash."""
    import bsddb3
    return bsddb3.hashopen(*args)
def open_dbhash(*args):
    """Open a bsddb hash.  Don't use this on Windows, unless Python 2.3 or
    greater is used, in which case bsddb3 is actually named bsddb."""
    from spambayes.port import bsddb
    return bsddb.hashopen(*args)
def open_gdbm(*args):
    """Open a gdbm database."""
    from spambayes.port import gdbm
    if gdbm is not None:
        return gdbm.open(*args)
    raise ImportError("gdbm not available")
def open_best(*args):
    if sys.platform == "win32":
        funcs = [open_db3hash, open_gdbm]
        if sys.version_info >= (2, 3):
            funcs.insert(0, open_dbhash)
    else:
        funcs = [open_db3hash, open_dbhash, open_gdbm]
    for f in funcs:
        try:
            return f(*args)
        except ImportError:
            pass
    raise error("No dbm modules available!")
open_funcs = {
    "best": open_best,
    "db3hash": open_db3hash,
    "dbhash": open_dbhash,
    "gdbm": open_gdbm,
    }
def open(db_name, mode):
    if os.path.exists(db_name) and \
       options.default("globals", "dbm_type") != \
       options["globals", "dbm_type"]:
        dbm_type = whichdb.whichdb(db_name)
        if (sys.platform == "win32" and
            sys.version_info < (2, 3) and
            dbm_type == "dbhash"):
            dbm_type = "db3hash"
    else:
        dbm_type = options["globals", "dbm_type"].lower()
    f = open_funcs.get(dbm_type)
    if f is None:
        raise error("Unknown dbm type: %s" % dbm_type)
    return f(db_name, mode)
