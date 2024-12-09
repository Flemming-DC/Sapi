from collections import namedtuple
from sapi._test import QueryError


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
            SELECT col0_1, col0_2, col00_2 FROM tab0
            JOIN tab00 USING (tab0_id))
        SELECT
            cte.col00_2,
            col10_2,
            (SELECT count(col20_2) FROM tab20)
        --FROM tree
        --join cte ON tree.col_1 = cte.col0_1
        FROM cte
        join tab ON tab.col_1 = cte.col0_1
        JOIN tab1 USING (tab_id)
        JOIN tab10 USING (tab1_id)
    """)

case2 = Case( # select no columns
    sapi = "select 1 from tree",
    expected_sql = QueryError)

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
    col1_1_, 
    col_2_, 
    col_2
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
    col1_1_,
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
    col1_1_,
    col0_1_,
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
    col1_1_,
    col0_1_,
    col1_1,
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
    col_1__
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
    expected_sql = QueryError)

case9 = Case(
    sapi = """
select sht__.col_1__
from tree_
from tree using (sht___id)
    """,
    expected_sql = QueryError)

delim = '\n;\n'

case10 = Case( # multi query
    sapi = case1.sapi + delim + case3.sapi,
    expected_sql = case1.expected_sql + delim + case3.expected_sql,
    )

case11 = Case( # multi query
    sapi = case3.sapi + delim + case4.sapi + delim + case5.sapi + delim,
    expected_sql = case3.expected_sql + delim + case4.expected_sql + delim + case5.expected_sql + delim,
    )

case12 = Case( # leading junk and multi query
    sapi = '''

1scscd
2scscd

3scscd
4hn

select 1 

from collections import namedtuple
from sapi._internals.token_tree import ParserError

# -------- define cases -------- #

Case = namedtuple('Case', ['sapi', 'expected_sql'])

case1 = Case( # cte, subquery and comments
    
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
    ;
    select 1
''',
    expected_sql = '''

1scscd
2scscd

3scscd
4hn

select 1 

from collections import namedtuple
from sapi._internals.token_tree import ParserError

# -------- define cases -------- #

Case = namedtuple('Case', ['sapi', 'expected_sql'])

case1 = Case( # cte, subquery and comments
    
        WITH cte AS (
            SELECT col0_1, col0_2, col00_2 FROM tab0
            JOIN tab00 USING (tab0_id))
        SELECT
            cte.col00_2,
            col10_2,
            (SELECT count(col20_2) FROM tab20)
        --FROM tree
        --join cte ON tree.col_1 = cte.col0_1
        FROM cte
        join tab ON tab.col_1 = cte.col0_1
        JOIN tab1 USING (tab_id)
        JOIN tab10 USING (tab1_id)
    ;
    select 1
'''
    )


case13 = Case( # empty string
    sapi = f"""{case1.sapi}
    ;
    --alter table xx;
    """,
    expected_sql = f"""{case1.expected_sql}
    """)

case14 = Case( # dual_key
    sapi = """
select dual_pk_col, dual_fk_col
from dual_key
    """,
    expected_sql = """
select dual_pk_col, dual_fk_col
from dual_fk 
join dual_pk using (dual_pk_id1, dual_pk_id2)
    """)

case15 = Case( # historic
    sapi = """
select historic_col1, 1 * 1
from historic
where historic_col2 != '' and 1 = 1 * 1
    """,
    expected_sql = """
select historic_col1, 1 * 1
from historic1
JOIN historic2 ON persistent2_id = persistent1_id and from_date2 < to_date2 and from_date1 < to_date1
where historic_col2 != '' and 1 = 1 * 1
    """)

case16 = Case( # select * from dual_key
    sapi = """
select *
from dual_key
    """,
    expected_sql = QueryError)

case17 = Case( # alias and blank tree
    sapi = """
WITH cte AS (
    SELECT col0_1, col0_2, col00_2 as b 
    FROM tree
)
SELECT 
    cte.b,
    cte.col0_2
FROM cte 
join tree ON tree.col_1 = cte.col0_1
    """,
    expected_sql = QueryError)


case18 = Case( # alias and blank tree
    sapi = """
WITH cte AS (
    SELECT col0_1, col0_2, col00_2 as b 
    FROM tree
)
SELECT 
    cte.b,
    cte.col0_2,
    tab.col_1
FROM cte 
join tree ON tree.col_1 = cte.col0_1
    """,
    expected_sql = """
WITH cte AS (
    SELECT col0_1, col0_2, col00_2 as b 
    FROM tab0
    JOIN tab00 USING (tab0_id))
SELECT 
    cte.b,
    cte.col0_2,
    tab.col_1
FROM cte
join tab ON tab.col_1 = cte.col0_1
""")


# empty_case = Case(
#     sapi = """
#     """,
#     expected_sql = """
#     """)

select_cases = [case1, case3, case4, case5, case6, case7, case10, case11, case12, case13, case14, case15, case18] 
select_error_cases = [case2, case8, case9, case16, case17]
non_executable_selects = [case12]
# print(f"select test cases = {len(select_cases) + len(select_error_cases) + len(non_executable_selects)}")

# select_cases = [] 
# select_error_cases = []
# non_executable_selects = []



