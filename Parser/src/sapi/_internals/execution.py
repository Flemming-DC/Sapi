import atexit
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Any, Type
from types import TracebackType
from sapi._internals import parser
from sapi._internals.db_contact.data_model import DataModel
from sapi._internals.db_contact.dialect import Dialect
from sapi._internals.db_contact import pep249_database_api_spec_v2 as pep


class CommitPolicy(Enum):
    AutoCommit = auto()
    ManualCommit = auto()
    OnTransactionSuccess = auto()


class QueryResult: 
    def __init__(_, cursor: pep.Cursor): _._cursor = cursor
    
    def rows(_): # specify return type
        return _._cursor.fetchall()
    
    # evt. commit (with fetch included, if necessary)


@dataclass
class Database:
    dialect: Dialect # (this is already inside model)
    startup_script: str = ""
    sapi_sys_schema: str = "sapi_sys"
    commit_policy: CommitPolicy = CommitPolicy.OnTransactionSuccess
    QueryResult_: Type[QueryResult] = QueryResult
    
    connect_args:   list[Any]      = field(default_factory = list)
    connect_kwargs: dict[str, Any] = field(default_factory = dict)
    cursor_args:    list[Any]      = field(default_factory = list)
    cursor_kwargs:  dict[str, Any] = field(default_factory = dict)

    _data_model: DataModel = None

    # def data_model(_) -> DataModel:
    #     if _._data_model is None: 
    #         _._data_model = DataModel.from_database(_.dialect, **_.connect_kwargs)
    #     return _._data_model

    def setup(_, cursor: pep.Cursor):
        if _._data_model is None: 
            _._data_model = DataModel.from_database(_.dialect, cursor, _.sapi_sys_schema)

    def data_model(_): 
        if _._data_model is None: raise Exception("---")
        return _._data_model


class Transaction: 
    default_database: Database | None = None

    def __init__(_, database: Database = None, read_only: bool = False): # probably pass con-info to connect function
        # evt. handle read_only differently
        _._con = None # _._con is None iff destructor doesn't need to close connection. 
        if database is None: database = Transaction.default_database 
        if database is None: raise TypeError(f"{Transaction.__name__} " 
            "requires a database as an input, since dependencies.default_database is None")
        
        _._con: pep.Connection = database.dialect.connect(*database.connect_args, **database.connect_kwargs)
        atexit.register(_._automatic_cleanup)
        if read_only: database.dialect.set_to_read_only(_._con)
        _._cursor: pep.Cursor = _._con.cursor(*database.cursor_args, **database.cursor_kwargs)
        _._cursor.execute(database.startup_script)
        _._con.commit()
        database.setup(_._cursor)
        # _._data_model = DataModel.from_database(database.dialect, _._cursor)
        _._database = database



    def connection(_): return _._con
    def cursor(_): return _._cursor
    def commit(_): _._con.commit()
    def __del__(_): _._automatic_cleanup()
    def __enter__(_): return _
    def __exit__(_, exc_type: Type[BaseException]|None, exc_value: BaseException|None, exc_traceback: TracebackType|None): 
        if exc_type is None and _._database.commit_policy == CommitPolicy.OnTransactionSuccess:
            _._con.commit()
        _._automatic_cleanup()

    def _automatic_cleanup(_):
        "Gets called by destructor (unreliable), by with-statement exit and by program exit."
        if _._con:
            _._con.close()
            _._con = None

    def execute(_, query: str, *args, **kwargs) -> QueryResult:
        query = parser.parse(query, _._database.data_model(), str)
        return _.execute_plain_sql(query, *args, **kwargs)

    def execute_plain_sql(_, sql_query: str, *args, **kwargs) -> QueryResult:
        _._cursor.execute(sql_query, *args, **kwargs)
        if _._database.commit_policy == CommitPolicy.AutoCommit: 
            _._con.commit()
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
