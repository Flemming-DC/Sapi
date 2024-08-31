from collections import namedtuple


Case = namedtuple('Case', ['sapi', 'expected_sql'])

case1 = Case( # cte, subquery and comments
    sapi = """
        WITH cte AS (
            SELECT COL0_1, COL0_2, COL00_2 FROM TREE
        )
        SELECT 
            cte.COL00_2,
            COL10_2,
            (SELECT sum(COL20_2) FROM TREE)
        --FROM TREE
        --join cte ON TREE.COL_1 = cte.COL0_1
        FROM cte 
        join TREE ON TREE.COL_1 = cte.COL0_1
    """,
    expected_sql = """
        WITH cte AS (
            SELECT TAB0.COL0_1, TAB0.COL0_2, TAB00.COL00_2 FROM TAB0
            JOIN TAB00 USING (TAB0_id))
        SELECT
            cte.COL00_2,
            TAB10.COL10_2,
            (SELECT sum TAB20.COL20_2) FROM TAB20)
        --FROM TREE
        --join cte ON TREE.COL_1 = cte.COL0_1
        FROM cte
        join TAB ON TAB.COL_1 = cte.COL0_1
        JOIN TAB1 USING (TAB_id)
        JOIN TAB10 USING (TAB1_id)
    """)

case2 = Case( # select no columns (postgres only)
    sapi = "select 1 from TREE",
    expected_sql = "select 1")
# caseN = Case( # select no columns (oracle only)
#     sapi = "select 1 from A",
#     expected_sql = "select 1 from dual")

case3 = Case( # join multiple trees
    sapi = """
select 
    col1_1, 
    col_2, 
    COL_2, 
from TREE
join tree on tree.col_1 = TREE.COL_1
    """,
    expected_sql = """
select 
    tab1.col1_1, 
    tab.col_2, 
    TAB.COL_2, 
from TAB
join tab on tab.col_1 = TAB.COL_1
join tab1 using (tab_id)
    """)


case4 = Case(
    sapi = """
select
    col1_1,
    tab0.col0_1,
    tree.col1_2,
from tree
    """,
    expected_sql = """
select
    tab1.col1_1,
    tab0.col0_1,
    tab1.col1_2,
from tab0
join tab using (tab_id)
join tab1 using (tab_id)
    """)

# make a case for joining multiple trees via a using statement



case5 = Case(
    sapi = """
select
    col1_1,
    col0_1,
    tab1.col1_2,
from tab0
join tab using (tab_id)
join tab1 using (tab_id)
    """,
    expected_sql = """
select
    tab1.col1_1,
    tab0.col0_1,
    tab1.col1_2,
from tab0
join tab using (tab_id)
join tab1 using (tab_id)
    """)

case6 = Case(
    sapi = """
select
    col1_1,
    col0_1,
    COL1_1,
    some_view.col0_1,
    x
from tree
join TAB1 on TAB1.col1_1 = tree.col1_1
join some_view on some_view.col0_1 = tab0.col0_1
    """,
    expected_sql = """
select
    tab1.col1_1,
    tab0.col0_1,
    TAB1.COL1_1,
    some_view.col0_1,
    x
from tab0
JOIN tab USING (tab_id)
JOIN tab1 USING (tab_id)
join TAB1 on TAB1.col1_1 = tab1.col1_1
join some_view on some_view.col0_1 = tab0.col0_1
    """)


# empty_case = Case(
#     sapi = """
#     """,
#     expected_sql = """
#     """)

select_cases = [case1, case2, case3, case4, case5, case6]
# select_cases = []




