from engine import parser




if __name__ == '__main__':
    q = """
    WITH cte AS (
        SELECT a0_1, a0_2, a00_2 FROM A
    )
    SELECT 
        cte.a00_2,
        a10_2,
        (SELECT sum(a20_2) FROM A)
    --FROM A
    --join cte ON A.a_1 = cte.a0_1
    FROM cte 
    join A ON A.a_1 = cte.a0_1
    """
    # tab_in_cte: a00, a0
    # outer_tab: a, a1, a10
    # sub: a20
    res = """
    WITH cte AS (
        SELECT a0_1, a0_2, a00_2 
        FROM a00
        JOIN a0 ON a0.a0_1 = a00.a0_1
    )
    SELECT 
        cte.a00_2,
        a10_2,
        (SELECT sum(a20_2) FROM a20)
    FROM cte 
    JOIN a   ON a.a_1 = cte.a0_1
    JOIN a1  ON a1.a_1 = a.a_1
    JOIN a10 ON a10.a1_1 = a1.a1_1
    """
    # evt. bug: graps a0_2 from a0 instead of cte
    # should we auto_join the missing tables or all the tables?
    # suggested answer: all, unless prefix says otherwise
    trees = parser.parse(q)

    for tr in trees:
        print("--- tree ---")
        print(tr)




