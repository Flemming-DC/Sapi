from engine import parser



if __name__ == '__main__':
    # 'A' is a table tree containing (amongst others) the columns 
    # a0_1, a0_2, a00_2, a10_2, a20_2, a_1
    sapi_query = """
    WITH cte AS (
        SELECT a0_1, a0_2, a00_2 FROM A
    )
    SELECT 
        cte.a00_2,
        a10_2,
        (SELECT sum(a20_2) FROM A)
    -- comment
    /* comment */
    FROM cte 
    join A ON A.a_1 = cte.a0_1
    """
    sql = parser.parse(sapi_query)
    print("--- sql-str ---")
    print(sql)

