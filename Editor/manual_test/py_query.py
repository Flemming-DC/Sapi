import os
import sqlglot

class Query: ...
Query = str
# todo bvedbre TODO efwew MOO geerge

class A:
    v: int = 1

print('hi')
x = 1

a = "%s $s"

class _sapi:
    pg = str
# pg = _sapi.pg

# pg.read("select 1 from a").rows()
_sapi.read_pg("select 1 from a").rows()

import sapi
# class pg: ...
pg = "select 1 from a"
sapi.read(pg + " select 1 from a ").rows()
# sapi.read(pg + " select 1 from a ").rows()

# class PG: ...
PG = str
query = pg + """
    select 1 
    from a;
"""
query: PG = "select 1 from a"
query = PG("select 1 from a")
query.lower()


with sapi.Transaction() as tr:
    tr.pg.execute("select 1 from a").rows() #pg
    tr.execute_pg("select 1 from a").rows()
    tr.pg("select 1 from a").rows()


_sapi.pg("select 1 from a").read().rows()
_sapi.read_pg("select 1 from a").rows()
_sapi.pg.read("select 1 from a").rows()
_sapi.read.pg("select 1 from a").rows()
_sapi.pg.read("select 1 from a").rows()

# pg (=|\(|\+|,) whitespace string

s: PG = f"""
    WITH cte AS (
        select col0_1, col00_2 FROM tree
    )
    SELECT /* hegr */
        'hejsa',
        $$ multi
        line $$,
        123, true and false,
        cte.col00_2,  
        col10_2,
        (SELECT count(col20_2) FROM tree)
    --FROM tree
    --join cte ON tree.col_1 = cte.col0_1
    FROM cte
    join tree ON tree.col_1 = cte.col0_1
    ;

    alter table xx;
    """

import os

print('hi')

def foo():
    return 5 + 5
