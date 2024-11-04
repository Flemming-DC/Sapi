# from tools.embedding import sapi_lines
# from textwrap import dedent

# if __name__ == '__main__':
#     py_sapi_1 = '''
# class A: ...

# pg = ""
# class B: ...

# pg + """
# WITH cte AS (
#     SELECT col0_1, col00_2 FROM tree
# )
# SELECT /* hegr */
#     'vervre',
#     $$ multi
#     line $$,
#     123,
#     cte.col00_2,
#     col10_2,
#     (SELECT count(col20_2) FROM tree)
# --FROM tree
# --join cte ON tree.col_1 = cte.col0_1
# FROM cte 
# join tree ON tree.col_1 = cte.col0_1
# ;
# """

# x = 1
# class C: ...
# '''
    
#     py_sapi_2 = '''
# import os
# import sqlglot

# class Query: ...
# Query = str
# # todo bvedbre TODO efwew MOO geerge

# class A:
#     v: int = 1

# print('hi')
# x = 1

# a = "%s $s"

# class _sapi:
#     pg = str
# # pg = _sapi.pg

# # pg.read("select 1 from a").rows()
# _sapi.read_pg("select 1 from a").rows()

# import sapi
# # class pg: ...
# pg = "select 1 from a"
# sapi.read(pg + " select 1 from a ").rows()
# # sapi.read(pg + " select 1 from a ").rows()

# # class PG: ...
# PG = str
# query = pg + """
#     select 1 
#     from a;
# """
# query: PG = "select 1 from a"
# query = PG("select 1 from a")
# query.lower()


# with sapi.Transaction() as tr:
#     tr.pg.execute("select 1 from a").rows() #pg
#     tr.execute_pg("select 1 from a").rows()
#     tr.pg("select 1 from a").rows()


# _sapi.pg("select 1 from a").read().rows()
# _sapi.read_pg("select 1 from a").rows()
# _sapi.pg.read("select 1 from a").rows()
# _sapi.read.pg("select 1 from a").rows()
# _sapi.pg.read("select 1 from a").rows()

# # pg (=|\(|\+|,) whitespace string

# s: PG = f"""
#     WITH cte AS (
#         select col0_1, col00_2 FROM tree
#     )
#     SELECT /* hegr */
#         'hejsa',
#         $$ multi
#         line $$,
#         123, true and false,
#         cte.col00_2,  
#         col10_2,
#         (SELECT count(col20_2) FROM tree)
#     --FROM tree
#     --join cte ON tree.col_1 = cte.col0_1
#     FROM cte
#     join tree ON tree.col_1 = cte.col0_1
#     ;

#     alter table xx;
#     """

# import os

# print('hi')

# def foo():
#     return 5 + 5

# '''

#     _sapi_lines = sapi_lines(py_sapi_1.split('\n'))
#     sapi_code = '\n'.join(_sapi_lines)
#     # print(f"'''{sapi_code}'''")
#     sc = '''






# WITH cte AS (
#     SELECT col0_1, col00_2 FROM tree
# )
# SELECT /* hegr */
#     'vervre',
#     $$ multi
#     line $$,
#     123,
#     cte.col00_2,
#     col10_2,
#     (SELECT count(col20_2) FROM tree)
# --FROM tree
# --join cte ON tree.col_1 = cte.col0_1
# FROM cte 
# join tree ON tree.col_1 = cte.col0_1
# ;




# '''

#     a, b = dedent(sapi_code), dedent(sc)
#     A = '\n'.join(x.rstrip() for x in  a.split('\n'))
#     B = '\n'.join(x.rstrip() for x in  b.split('\n'))
#     assert A == B, ""


#     _sapi_lines = sapi_lines(py_sapi_2.split('\n'))
#     sapi_code = '\n'.join(_sapi_lines)
#     print(f"'''{sapi_code}'''")
#     sc = '''




















#                select 1 from a



#       select 1 from a
#                  select 1 from a
#                    select 1 from a




#     select 1
#     from a;

#              select 1 from a
#             select 1 from a





#                    select 1 from a
#            select 1 from a


#           select 1 from a
#                select 1 from a

#                select 1 from a





#     WITH cte AS (
#         select col0_1, col00_2 FROM tree
#     )
#     SELECT /* hegr */
#         'hejsa',
#         $$ multi
#         line $$,
#         123, true and false,
#         cte.col00_2,
#         col10_2,
#         (SELECT count(col20_2) FROM tree)
#     --FROM tree
#     --join cte ON tree.col_1 = cte.col0_1
#     FROM cte
#     join tree ON tree.col_1 = cte.col0_1
#     ;

#     alter table xx;









# '''

#     a, b = dedent(sapi_code), dedent(sc)
#     A = '\n'.join(x.rstrip() for x in  a.split('\n'))
#     B = '\n'.join(x.rstrip() for x in  b.split('\n'))
#     assert A == B, ""

#     print("done")        