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

    # forest = postgres_forest.setup_db_and_make_forest()
    data_model = runtime_model.make_datamodel()
    sql = sapi.parse(sapi_query, data_model, list[str])
    
    sql = [sql] if isinstance(sql, str) else sql
    for query in sql:
        print("--- sql-str ---")
        print(query)
    
        connection_info = postgres_model.get_connection_info()
        with psycopg.Connection.connect(**connection_info) as con:
            with con.cursor() as cur:
                cur.execute("set search_path to sapi_demo")
                data = cur.execute(query).fetchall()
                print("--- data ---")
                print(data)

def sapi_plugin():
    # ---------- Sapi Plugin ---------- #
    class SapiCursor(psycopg.Cursor):
        def execute(self, query, params = None, *, prepare = None, binary = None) -> SapiCursor:
            query = sapi.parse(query, return_type=str)
            return super().execute(query, params, prepare=prepare, binary=binary)

    # forest = postgres_forest.setup_db_and_make_forest()
    data_model = runtime_model.make_datamodel()
    sapi.dependencies.default_data_model = data_model

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
    with psycopg.Connection.connect(**connection_info, cursor_factory=SapiCursor) as con:
        with con.cursor() as cur:
            cur.execute("set search_path to sapi_demo")
            data = cur.execute(sapi_query).fetchall()
            print("--- data ---")
            print(data)


def nice_tooling():
    # ---------- Setup ---------- #
    database = sapi.Database(
        dialect = sapi.dialect.postgres(),
        startupScript = "set search_path to sapi_demo",
        connect_kwargs = postgres_model.get_connection_info(),
        )
    sapi.dependencies.default_database = database

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
        print("--- execute ---")
        print(data)

    data = sapi.read(select_query).rows()
    print("--- read ---")
    print(data)


if __name__ == '__main__':
    nice_tooling()



