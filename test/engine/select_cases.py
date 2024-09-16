from collections import namedtuple
from engine.token_tree import ParserError
from engine.externals.database_py.forest import Forest, Tree, Table

# -------- define runtime forest -------- #
_tree = Tree(
    tables=[
        Table(name='sht__', parent='tab',  columns=['col_1__', 'col_2__', 'sht___id', 'tab__id', 'tab_id']), 
        Table(name='tab',   parent=None,   columns=['col_1', 'col_2', 'tab_id']), 
        Table(name='tab0',  parent='tab',  columns=['col0_1', 'col0_2', 'shc', 'tab0_id', 'tab1__id', 'tab_id']), 
        Table(name='tab00', parent='tab0', columns=['col00_1', 'col00_2', 'tab00_id', 'tab0_id']), 
        Table(name='tab01', parent='tab0', columns=['col01_1', 'col01_2', 'tab01_id', 'tab0_id']), 
        Table(name='tab1',  parent='tab',  columns=['col1_1', 'col1_2', 'shc', 'tab0__id', 'tab1_id', 'tab_id']), 
        Table(name='tab10', parent='tab1', columns=['col10_1', 'col10_2', 'tab10_id', 'tab1_id']), 
        Table(name='tab2',  parent='tab',  columns=['col2_1', 'col2_2', 'tab2_id', 'tab_id']), 
        Table(name='tab20', parent='tab2', columns=['col20_1', 'col20_2', 'tab20_id', 'tab2_id']), 
        Table(name='tab21', parent='tab2', columns=['col21_1', 'col21_2', 'tab21_id', 'tab2_id']),
        ], 
    name='tree', schema='sapi_demo')

_tree_ = Tree(
    tables=[
        Table(name='sht__', parent='tab_', columns=['col_1__', 'col_2__', 'sht___id', 'tab__id', 'tab_id']), 
        Table(name='tab_',  parent=None,   columns=['col_1_', 'col_2_', 'tab__id']), 
        Table(name='tab0_', parent='tab_', columns=['col0_1_', 'col0_2_', 'shc_', 'tab0__id', 'tab1_id', 'tab__id']), 
        Table(name='tab1_', parent='tab_', columns=['col1_1_', 'col1_2_', 'shc_', 'tab0_id', 'tab1__id', 'tab__id']),
        ], 
    name='tree_', schema='sapi_demo')

# forest = Forest([_tree, _tree_])
with open('../sapi_secret/pg_password.txt') as f:
    password = f.read()
forest = Forest.from_database(host='localhost', port = 5432, dbname = 'postgres', user = 'postgres', password=password)


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
            (SELECT sum(col20_2) FROM tree)
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
            (SELECT sum tab20.col20_2) FROM tab20)
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
    col_2, 
from tree
join tree_ on tree_.col_1_ = tree.col_1
    """,
    expected_sql = """
select 
    tab1_.col1_1_, 
    tab_.col_2_, 
    tab.col_2, 
from tab
join tab_ on tab_.col_1_ = tab.col_1
join tab1_ using (tab_id)
    """)


case4 = Case(
    sapi = """
select
    col1_1_,
    tab0_.col0_1_,
    tree_.col1_2_,
from tree_
    """,
    expected_sql = """
select
    tab1_.col1_1_,
    tab0_.col0_1_,
    tab1_.col1_2_,
from tab0_
join tab_ using (tab_id)
join tab1_ using (tab_id)
    """)

# make a case for joining multiple trees via a using statement



case5 = Case(
    sapi = """
select
    col1_1_,
    col0_1_,
    tab1_.col1_2_,
from tab0_
join tab_ using (tab_id)
join tab1_ using (tab_id)
    """,
    expected_sql = """
select
    tab1_.col1_1_,
    tab0_.col0_1_,
    tab1_.col1_2_,
from tab0_
join tab_ using (tab_id)
join tab1_ using (tab_id)
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
join tab1 on tab1.col1_1_ = tree_.col1_1_
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
JOIN tab_ USING (tab_id)
JOIN tab1_ USING (tab_id)
join tab1 on tab1.col1_1_ = tab1_.col1_1_
join some_view on some_view.col0_1_ = tab0_.col0_1_
    """)

case7 = Case(
    sapi = """
select
    col_1__
from tree_ 
where true
order by tab0_.shc
    """,
    expected_sql = """
select
    sht__.col_1__
from sht__
join tab_ using (tab_id)
join tab0_ using (tab_id)
where true
order by tab0_.shc
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
from tree using (shT3_id)
    """,
    expected_sql = ParserError)


# empty_case = Case(
#     sapi = """
#     """,
#     expected_sql = """
#     """)

select_cases = [case1, case2, case3, case4, case5, case6, case7]
select_error_cases = [case8, case9]
# select_cases = [] 
# select_error_cases = []



