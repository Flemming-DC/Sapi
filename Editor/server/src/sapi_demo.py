import sapi
import runtime_model

def get_sql() -> str:
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
    forest = runtime_model.make_datamodel()
    sql = sapi.parse(sapi_query, forest)
    return sql




