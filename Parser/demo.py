import psycopg
import sapi
from test import postgres_model, runtime_model

if __name__ == '__main__':
    
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
    forest = runtime_model.make_datamodel()
    sql = sapi.parse(sapi_query, forest)
    
    print("--- sql-str ---")
    print(sql)
    
    connection_info = postgres_model.get_connection_info()
    with psycopg.Connection.connect(**connection_info) as con:
        with con.cursor() as cur:
            cur.execute("set search_path to sapi_demo")
            data = cur.execute(sql).fetchall()
            print("--- data ---")
            print(data)
