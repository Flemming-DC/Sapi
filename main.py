from engine import parser
from test.engine import runtime_forest, postgres_forest

if __name__ == '__main__':
    
    sapi_query = """
        WITH cte AS (
            SELECT col0_1, col0_2, col00_2 FROM tree
        )
        SELECT 
            cte.col00_2,
            col10_2,
            (SELECT sum(col20_2) FROM tree)
        --comment from from 
        FROM cte 
        join tree ON tree.col_1 = cte.col0_1
        """
    
    # forest = postgres_forest.setup_db_and_make_forest()
    forest = runtime_forest.make_forest()
    sql = parser.parse(sapi_query, forest)

    print("--- sql-str ---")
    print(sql)
    
