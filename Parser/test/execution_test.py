

from __future__ import annotations
import warnings
import psycopg
import traceback
from typing import Callable, Type
import sapi
from . import demo_pg_model, runtime_model
from sapi._internals.error import QueryError, TestError

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
    if not isinstance(sql_list, list): raise TestError("")

    for query in sql_list:
        if not isinstance(query, str): raise TestError("")
    
        connection_info = demo_pg_model.get_connection_info()
        with psycopg.Connection.connect(**connection_info) as con, con.cursor() as cur:
            demo_pg_model.set_demo_searchpath(cur)
            _ = cur.execute(query).fetchall()


def _test_sapi_plugin():
    # ---------- Sapi Plugin ---------- #
    class SapiCursor(psycopg.Cursor):
        data_model = runtime_model.make_datamodel()
        def execute(self, query, params = None, *, prepare = None, binary = None) -> SapiCursor:
            query = sapi.parse(query, SapiCursor.data_model, return_type=str)
            return super().execute(query, params, prepare=prepare, binary=binary)

    # ---------- Normal Boilerplate + Execute Query---------- #
    connection_info = demo_pg_model.get_connection_info()
    with psycopg.Connection.connect(**connection_info, cursor_factory=SapiCursor) as con, con.cursor() as cur:
        demo_pg_model.set_demo_searchpath(cur)
        _ = cur.execute(_select_query).fetchall()


def _test_nice_tooling():
    # ---------- Setup ---------- #
    database = sapi.Database(
        dialect = sapi.dialect.postgres(),
        sys_schema = demo_pg_model.sys_schema(),
        startup_script = f"set search_path to {demo_pg_model.demo_schema()}",
        connect_kwargs = demo_pg_model.get_connection_info(),
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
        sys_schema = demo_pg_model.sys_schema(),
        startup_script = f"set search_path to {demo_pg_model.demo_schema()}",
        connect_kwargs = demo_pg_model.get_connection_info(),
        )
    sapi.Transaction.default_database = database

    # ---------- Query ---------- #
    insert_query = "insert into tab (tab_id, col_1, col_2) values (1, 'col_1', 'col_2');"
    with warnings.catch_warnings(record=True): # captures "insert not yet implemented warning"
        with sapi.Transaction(read_only=True) as tr:
            _check_raises(lambda: tr.execute(insert_query))
        _check_raises(lambda: sapi.read(insert_query))


def _check_raises(func: Callable):
    try:   func()
    except QueryError: return True
    except psycopg.errors.Error: return True
    except Exception: 
        print("------ Incorrect exception type ------")
        traceback.print_exc()
        print("------")
    raise TestError(f"{func} did not raise the expected error.")



if __name__ == '__main__':
    run_tests()
    print("Tests Passed")
