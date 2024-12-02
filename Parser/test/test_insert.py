import json
import psycopg
import sapi
from test import demo_pg_model, runtime_model, comparison

def _test_insert_into_tree() -> dict:
    with open('tab_.json') as f:
        tree_dict: dict = json.load(f)

    connection_info = demo_pg_model.get_connection_info()
    with psycopg.Connection.connect(**connection_info) as con, con.cursor() as cur:
        cur.execute("set search_path to sapi_demo")
        sapi.insert_into_tree(cur, tree_dict)
    
def _test_parse_insert():
    with open('tab_.json') as f:
        tree_json = f.read()
    sapi_query = f"""
        insert into tree_
        values ($${tree_json}$$)
        """
    expected_sql = """
        insert into tab_ (col_1_, col_2_)
        select 'from json', 'from json'
        ;
        with parent as (select max(tab__id) as id from tab_)
        insert into tab0_ (tab__id, col0_1_, col0_2_, shc_)
        select parent.id, 'from json', 'from json', 'from json' from parent
        ;
        with parent as (select max(tab__id) as id from tab_)
        insert into tab1_ (tab__id, col1_1_, col1_2_, shc_)
        select parent.id, 'from json', 'from json', 'from json' from parent
        ;
        with parent as (select max(tab__id) as id from tab_)
        insert into sht__ (tab__id, tab_id, col_1__, col_2__)
        select parent.id, 1, 'from json', 'from json' from parent
        """
    data_model = runtime_model.make_datamodel()
    actual_sql = sapi.parse(sapi_query, data_model, str)
    comparison.assert_match(sapi_query, actual_sql, expected_sql)


def run_tests():
    _test_insert_into_tree()
    _test_parse_insert()
