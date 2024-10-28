from __future__ import annotations
import psycopg
import sapi
from test import postgres_model, runtime_model

def low_level_usage():
    sapi_query = """
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

    # sapi.setup_sapi(dialect.postgres(), **connection_info)
    # data_model = postgres_forest.setup_db_and_make_forest()
    data_model = runtime_model.make_datamodel()
    sql = sapi.parse(sapi_query, data_model, list[str])
    
    sql = [sql] if isinstance(sql, str) else sql
    for query in sql:
        print("--- sql-str ---")
        print(query)
    
        connection_info = postgres_model.get_connection_info()
        with psycopg.Connection.connect(**connection_info) as con, con.cursor() as cur:
            cur.execute("set search_path to sapi_demo")
            data = cur.execute(query).fetchall()
            print("--- low_level ---")
            print(data)

def sapi_plugin():
    # ---------- Sapi Plugin ---------- #
    class SapiCursor(psycopg.Cursor):
        data_model = runtime_model.make_datamodel()
        def execute(self, query, params = None, *, prepare = None, binary = None) -> SapiCursor:
            query = sapi.parse(query, SapiCursor.data_model, return_type=str)
            return super().execute(query, params, prepare=prepare, binary=binary)

    # sapi.setup_sapi(dialect.postgres(), **connection_info)
    # sapi.dependencies.default_data_model = data_model

    # ---------- Normal Boilerplate + Execute Query---------- #
    sapi_query = """
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
    
    connection_info = postgres_model.get_connection_info()
    with psycopg.Connection.connect(**connection_info, cursor_factory=SapiCursor) as con, con.cursor() as cur:
        cur.execute("set search_path to sapi_demo")
        data = cur.execute(sapi_query).fetchall()
        print("--- plugin ---")
        print(data)


def nice_tooling():
    # ---------- Setup ---------- #
    database = sapi.Database(
        dialect = sapi.dialect.postgres(),
        startup_script = "set search_path to sapi_demo",
        connect_kwargs = postgres_model.get_connection_info(),
        )
    sapi.Transaction.default_database = database

    # ---------- Query ---------- #
    select_query = """
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
    insert_query = "insert into tab (tab_id, col_1, col_2) values (1, 'col_1', 'col_2');"

    with sapi.Transaction() as tr:
        data = tr.execute(select_query).rows()
        print("--- transaction ---")
        print(data)

    data = sapi.read(select_query).rows()
    print("--- read ---")
    print(data)


if __name__ == '__main__':
    nice_tooling()
    sapi_plugin()

# cleanup connection-info references in datamodel
# cleanup default datamodel
# support connection pooling
# extend QueryResult / Formatter
