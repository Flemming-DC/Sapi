from engine import parser
from engine.externals.database_py.forest import Forest
# from engine.token_tree import TokenTree


if __name__ == '__main__':
    # 'A' is a table tree containing (amongst others) the columns 
    # a0_1, a0_2, a00_2, a10_2, a20_2, a_1
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
    # trees = [...]
    # trees = load_trees_from_db(connection_info, dialect)
    # forest.from(trees) # evt. also dialect
    # forest.from(connection_info, dialect)
    with open('../sapi_secret/pg_password.txt') as f:
        password = f.read()
    forest = Forest.from_database(host='localhost', port = 5432, dbname = 'postgres', user = 'postgres', password=password)

    sql = parser.parse(sapi_query, forest) # datamodel
    print("--- sql-str ---")
    print(sql)
    
