from collections import namedtuple
from sapi.token_tree import ParserError

# -------- define cases -------- #

Case = namedtuple('Case', ['sapi', 'expected_sql'])

case1 = Case( # cte, subquery and comments
    sapi = """
        WITH cte AS (
            SELECT col0_1, col0_2, col00_2 FROM tree
        )
        SELECT 
            cte.col00_2,
            col10_2,
            (SELECT count(col20_2) FROM tree)
        --FROM tree
        --join cte ON tree.col_1 = cte.col0_1
        FROM cte 
        join tree ON tree.col_1 = cte.col0_1
    """,
    expected_sql = """
        WITH cte AS (
            SELECT tab0.col0_1, tab0.col0_2, tab00.col00_2 FROM tab0
            JOIN tab00 USING (tab0_id))
        SELECT
            cte.col00_2,
            tab10.col10_2,
            (SELECT count(tab20.col20_2) FROM tab20)
        --FROM tree
        --join cte ON tree.col_1 = cte.col0_1
        FROM cte
        join tab ON tab.col_1 = cte.col0_1
        JOIN tab1 USING (tab_id)
        JOIN tab10 USING (tab1_id)
    """)

case2 = Case( # select no columns (postgres only)
    sapi = "select 1 from tree",
    expected_sql = "select 1")
# caseN = Case( # select no columns (oracle only)
#     sapi = "select 1 from A",
#     expected_sql = "select 1 from dual")

case3 = Case( # join multiple trees
    sapi = """
select 
    col1_1_, 
    col_2_, 
    col_2
from tree
join tree_ on tree_.col_1_ = tree.col_1
    """,
    expected_sql = """
select 
    tab1_.col1_1_, 
    tab_.col_2_, 
    tab.col_2
from tab
join tab_ on tab_.col_1_ = tab.col_1
join tab1_ using (tab__id)
    """)


case4 = Case(
    sapi = """
select
    col1_1_,
    tab0_.col0_1_,
    tree_.col1_2_
from tree_
    """,
    expected_sql = """
select
    tab1_.col1_1_,
    tab0_.col0_1_,
    tab1_.col1_2_
from tab0_
join tab_ using (tab__id)
join tab1_ using (tab__id)
    """)

# make a case for joining multiple trees via a using statement



case5 = Case(
    sapi = """
select
    col1_1_,
    col0_1_,
    tab1_.col1_2_
from tab0_
join tab_ using (tab__id)
join tab1_ using (tab__id)
    """,
    expected_sql = """
select
    tab1_.col1_1_,
    tab0_.col0_1_,
    tab1_.col1_2_
from tab0_
join tab_ using (tab__id)
join tab1_ using (tab__id)
    """)

case6 = Case(
    sapi = """
select
    col1_1_,
    col0_1_,
    col1_1,
    some_view.col0_1_,
    x
from tree_
join tab1 on tab1.col1_1 = tree_.col1_1_
join some_view on some_view.col0_1_ = tab0_.col0_1_
    """,
    expected_sql = """
select
    tab1_.col1_1_,
    tab0_.col0_1_,
    tab1.col1_1,
    some_view.col0_1_,
    x
from tab0_
JOIN tab_ USING (tab__id)
JOIN tab1_ USING (tab__id)
join tab1 on tab1.col1_1 = tab1_.col1_1_
join some_view on some_view.col0_1_ = tab0_.col0_1_
    """)

case7 = Case(
    sapi = """
select
    col_1__
from tree_ 
where true
order by tab0_.shc_
    """,
    expected_sql = """
select
    sht__.col_1__
from sht__
join tab_ using (tab__id)
join tab0_ using (tab__id)
where true
order by tab0_.shc_
    """)

case8 = Case(
    sapi = """
select shc_
from tree_ 
    """,
    expected_sql = ParserError)

case9 = Case(
    sapi = """
select sht__.col_1__
from tree_
from tree using (sht___id)
    """,
    expected_sql = ParserError)


# empty_case = Case(
#     sapi = """
#     """,
#     expected_sql = """
#     """)

# select_cases = [case1, case2, case3, case4, case5, case6, case7]
select_cases = [case1, case2, case3, case4, case5, case6, case7]
select_error_cases = [case8, case9]
# select_cases = [] 
# select_error_cases = []



