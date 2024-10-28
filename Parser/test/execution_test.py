

from __future__ import annotations
import warnings
from typing import Callable, Type
import psycopg
import sapi
from . import postgres_model, runtime_model

_select_query = """
    WITH cte AS (
        SELECT col0_1, col0_2, col00_2 FROM tree
    )
    SELECT 
        cte.col00_2,
        col10_2,
        (SELECT count(col20_2) FROM tree)
    -- here we have a select query. sapi parsed to sql
    FROM cte 
    join tree ON tree.col_1 = cte.col0_1
    """


def run_tests():
    _test_low_level_usage()
    _test_nice_tooling()
    _test_sapi_plugin()
    _test_readonly()


def _test_low_level_usage():
    data_model = runtime_model.make_datamodel()
    sql_list = sapi.parse(_select_query, data_model, list[str])
    assert isinstance(sql_list, list), ""

    for query in sql_list:
        assert isinstance(query, str), ""
    
        connection_info = postgres_model.get_connection_info()
        with psycopg.Connection.connect(**connection_info) as con, con.cursor() as cur:
            cur.execute("set search_path to sapi_demo")
            _ = cur.execute(query).fetchall()


def _test_sapi_plugin():
    # ---------- Sapi Plugin ---------- #
    class SapiCursor(psycopg.Cursor):
        data_model = runtime_model.make_datamodel()
        def execute(self, query, params = None, *, prepare = None, binary = None) -> SapiCursor:
            query = sapi.parse(query, SapiCursor.data_model, return_type=str)
            return super().execute(query, params, prepare=prepare, binary=binary)

    # ---------- Normal Boilerplate + Execute Query---------- #
    connection_info = postgres_model.get_connection_info()
    with psycopg.Connection.connect(**connection_info, cursor_factory=SapiCursor) as con, con.cursor() as cur:
        cur.execute("set search_path to sapi_demo")
        _ = cur.execute(_select_query).fetchall()


def _test_nice_tooling():
    # ---------- Setup ---------- #
    database = sapi.Database(
        dialect = sapi.dialect.postgres(),
        startup_script = "set search_path to sapi_demo",
        connect_kwargs = postgres_model.get_connection_info(),
        )
    sapi.Transaction.default_database = database

    # ---------- Query ---------- #
    with sapi.Transaction() as tr:
        _ = tr.execute(_select_query).rows()
    _ = sapi.read(_select_query).rows()


def _test_readonly():
    # ---------- Setup ---------- #
    database = sapi.Database(
        dialect = sapi.dialect.postgres(),
        startup_script = "set search_path to sapi_demo",
        connect_kwargs = postgres_model.get_connection_info(),
        )
    sapi.Transaction.default_database = database

    # ---------- Query ---------- #
    insert_query = "insert into tab (tab_id, col_1, col_2) values (1, 'col_1', 'col_2');"
    with warnings.catch_warnings(record=True): # captures "insert not yet implemented warning"
        with sapi.Transaction(read_only=True) as tr:
            assert _raises(lambda: tr.execute(insert_query))
        assert _raises(lambda: sapi.read(insert_query))


def _raises(func: Callable, error_type: Type[Exception] = Exception):
    try:   func()
    except error_type: return True
    except Exception: ...
    return False



if __name__ == '__main__':
    run_tests()
    print("Tests Passed")
