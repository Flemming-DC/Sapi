import atexit
from dataclasses import dataclass, field
from typing import Any, Type
from sapi._internals import parser
from sapi._internals.db_contact.data_model import DataModel
from sapi._internals.db_contact.dialect import Dialect
from sapi._internals.db_contact import pep249_database_api_spec_v2 as pep
from . import dependencies

# try: # The SapiCursor is a postgress only feature.
#     import psycopg
#     class SapiCursor(psycopg.Cursor):
#         def execute(self, query, params = None, *, prepare = None, binary = None) -> SapiCursor:
#             query = parser.parse(query, return_type=str)
#             return super().execute(query, params, prepare=prepare, binary=binary)
# except ModuleNotFoundError: ...

    
class QueryResult: 
    def __init__(_, cursor: pep.Cursor): _._cursor = cursor
    
    def rows(_): # specify return type
        return _._cursor.fetchall()


@dataclass
class Database:
    dialect: Dialect # (this is already inside model)
    # connection_info: dict[str, Any]
    startupScript: str # evt. replace with Query
    
    connect_args:   list[Any]      = field(default_factory = list)
    connect_kwargs: dict[str, Any] = field(default_factory = dict)
    cursor_args:    list[Any]      = field(default_factory = list)
    cursor_kwargs:  dict[str, Any] = field(default_factory = dict)

    data_model: DataModel = None # load lazily. make this private. 
                          # besides, it should probably take a connection, not connection_info as input
    QueryResult_: Type[QueryResult] = QueryResult


class Transaction: 

    def __init__(_, database: Database = None, read_only: bool = False): # probably pass con-info to connect function
        # evt. handle read_only differently
        _._con = None # _._con is None iff destructor doesn't need to close connection. 
        if database is None: database = dependencies.default_database 
        if database is None: raise TypeError(
            "Connection requires a database as an input, since dependencies.default_database is None")
        
        database.data_model = DataModel.from_database(database.dialect, **database.connect_kwargs) # messy. fix this.
        _._database = database
        _._con: pep.Connection = database.dialect.connect(*database.connect_args, **database.connect_kwargs)
        atexit.register(_._automatic_cleanup)
        if read_only: database.dialect.set_to_read_only(_._con)
        _._cursor: pep.Cursor = _._con.cursor(*database.cursor_args, **database.cursor_kwargs)
        _._cursor.execute(database.startupScript)



    def __del__(_): _._automatic_cleanup()
    def __enter__(_): return _
    def __exit__(_, exc_type, exc_value, exc_traceback): 
        # obey commit-policy
        _._automatic_cleanup()

    def _automatic_cleanup(_):
        "Gets called by destructor (unreliable), by with-statement exit and by program exit."
        if _._con:
            _._con.close()
            _._con = None

    def execute(_, query: str, *args, **kwargs) -> QueryResult:
        query = parser.parse(query, _._database.data_model, str)
        _._cursor.execute(query, *args, **kwargs)
        return _._database.QueryResult_(_._cursor)


# how to handle read for multiple databases?
_reader: Transaction = None # the read-only connection used by read

# how does args, kwargs fit with database?
# should query be a str or marked as type Query = str ?
def read(query: str, *args, **kwargs) -> QueryResult:
    global _reader
    if _reader is None: _reader = Transaction(read_only = True)
    return _reader.execute(query, *args, **kwargs)


# what about pooling?
# what about singleshot queries?
