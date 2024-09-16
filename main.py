from engine import parser
from engine.externals.database_py import dialect, forest


if __name__ == '__main__':
    
    sapi_query = """
        WITH cte AS (
            SELECT COL0_1, COL0_2, COL00_2 FROM TREE
        )
        SELECT 
            cte.COL00_2,
            COL10_2,
            (SELECT sum(COL20_2) FROM TREE)
        -- comment
        /* comment */
        FROM cte 
        join TREE ON TREE.COL_1 = cte.COL0_1
        """
    
    with open('../sapi_secret/pg_password.txt') as f:
        password = f.read()
    forest = forest.Forest.from_database(dialect.postgres(),
        host='localhost', port = 5432, dbname = 'postgres', user = 'postgres', password=password)
    
    sql = parser.parse(sapi_query, forest)

    print("--- sql-str ---")
    print(sql)
    
