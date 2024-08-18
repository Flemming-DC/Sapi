import sqlglot


# x = sqlglot.transpile("SELECT q'[don't]' from dual", read="oracle", write="postgres")
# y = x[0]

from sqlglot import parse_one, exp

# print all column references (a and b)
for column in parse_one("SELECT a, b + 1 AS c FROM d").find_all(exp.Column):
    print('column', column.alias_or_name)

# find all projections in select statements (a and c)
for select in parse_one("SELECT a, b + 1 AS c FROM d").find_all(exp.Select):
    for projection in select.expressions:
        print('Select', projection.alias_or_name)

# find all tables (x, y, z)
for table in parse_one("SELECT * FROM x JOIN y JOIN z").find_all(exp.Table):
    print('Table', table.name)

from sqlglot import parse_one
from sqlglot.expressions import Select, Insert, Update, Delete, Column, Table
# Select is Query is Expression

s: Select = parse_one("SELECT x FROM y")
a = s.from_("z").sql()
print(a)
# 'SELECT x FROM z'

q = """
    with cte as (SELECT a2.* from g)
    SELECT 1, a1.*, a2_2
    from g
    /*
    comment
    comment
    */
    join cte using (k)
    where a2_2 != 0 -- comment
    ;
    /*
    comment
    comment
    */
    SELECT 1
    """

s: Select = parse_one(q)
a = s.from_("z").sql()
print(a)


from sqlglot.dialects import Postgres, Oracle, SQLite
from sqlglot.executor import execute, Table as executor_Table # table here or in sqlglot.expressions
from sqlglot.executor.python import Python

tables = {
    "sushi": [
        {"id": 1, "price": 1.0},
        {"id": 2, "price": 2.0},
        {"id": 3, "price": 3.0},
    ],
    "order_items": [
        {"sushi_id": 1, "order_id": 1},
        {"sushi_id": 1, "order_id": 1},
        {"sushi_id": 2, "order_id": 1},
        {"sushi_id": 3, "order_id": 2},
    ],
    "orders": [
        {"id": 1, "user_id": 1},
        {"id": 2, "user_id": 2},
    ],
}


# from sqlglot.executor import Table as executor_Table
result: executor_Table = execute(
    """
    SELECT
      o.user_id,
      SUM(s.price) AS price
    FROM orders o
    JOIN order_items i
      ON o.id = i.order_id
    JOIN sushi s
      ON i.sushi_id = s.id
    GROUP BY o.user_id
    """,
    tables=tables
)

ast = parse_one("""
WITH cte AS (
  SELECT a FROM y
)
SELECT a FROM cte join z
""")
# ast = parse_one(q)
from sqlglot.optimizer.scope import build_scope
root = build_scope(ast)
tables = [
    source

    # Traverse the Scope tree, not the AST
    for scope in root.traverse()

    # `selected_sources` contains sources that have been selected in this scope, e.g. in a FROM or JOIN clause.
    # `alias` is the name of this source in this particular scope.
    # `node` is the AST node instance
    # if the selected source is a subquery (including common table expressions),
    #     then `source` will be the Scope instance for that subquery.
    # if the selected source is a table,
    #     then `source` will be a Table instance.
    for alias, (node, source) in scope.selected_sources.items()
    if isinstance(source, exp.Table)
]

for table in tables:
    print("table found by fancy approach", table)


for table in ast.find_all(exp.Table):
    print('Table found by simple approach:', table.name, ', depth = ', table.depth)

from sqlglot.optimizer.qualify import qualify
# prefixed_ast = qualify(ast) # returns unknown table error
# print(prefixed_ast)

from sqlglot.optimizer.scope import find_all_in_scope
from typing import Generator
from sqlglot.optimizer.scope import Scope
root = build_scope(ast)
# `find_all_in_scope` is similar to `Expression.find_all`, except it doesn't traverse into subqueries
# for column in find_all_in_scope(root.expression, exp.Column):
#     print(f"{column} => {root.sources[column.table]}") # Exception has occurred: KeyError 'a1'

columns: Generator = find_all_in_scope(root.expression, exp.Column)
columns: list[Column] = list(columns)
tables: str = [c.table for c in columns]
sources: dict[str, Scope] = root.sources
x: list[str] = list(root.sources.keys())
print(tables)
print(x)


print(1)
s1: Select = parse_one("SELECT 'This isn''t a date' from dual", read="oracle")
# print(2)
# s2: Select = parse_one("SELECT q'[This isn't a date]' from dual", read="oracle") # failed
print(3)
s3: Select = parse_one("SELECT 'This isn''t a date'", read="postgres")
print(4)
s4: Select = parse_one("SELECT $$This isn't a date$$", read="postgres")
print(5)
s5: Select = parse_one("SELECT $few$This isn't a date$few$", read="postgres")


""