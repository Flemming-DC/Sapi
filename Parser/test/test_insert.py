import json
import psycopg
import sapi
from test import demo_pg_model, runtime_model, comparison
from test.insert_cases import insert_cases, case_manual_pk


def run_tests():
    data_models = [runtime_model.make_datamodel(), demo_pg_model.setup_db_and_make_datamodel()]
    for model in data_models:
        _test_parse_insert(model)
        _test_case_manual_pk(model)
    _test_insert_into_tree()


def _test_parse_insert(data_model: sapi.DataModel):
    for sapi_query, expected_sql in insert_cases:
        actual_sql = sapi.parse(sapi_query, data_model, str)
        comparison.assert_match(sapi_query, actual_sql, expected_sql)


def _test_case_manual_pk(data_model: sapi.DataModel):
    connection_info = demo_pg_model.get_connection_info()
    with psycopg.Connection.connect(**connection_info) as con, con.cursor() as cur:
        demo_pg_model.set_demo_searchpath(cur)
        tab_manual_id  = cur.execute("select max(tab_manual_id)  as id from tab_manual ").fetchall()[0][0]
        tab0_manual_id = cur.execute("select max(tab0_manual_id) as id from tab0_manual").fetchall()[0][0]
    sapi_query, expected_sql = case_manual_pk(tab_manual_id, tab0_manual_id)
    actual_sql = sapi.parse(sapi_query, data_model, str)
    comparison.assert_match(sapi_query, actual_sql, expected_sql)


def _test_insert_into_tree() -> dict:
    with open('test/tab_.json') as f:
        tree_dict: dict = json.load(f)

    # connection_info = None # 
    connection_info = demo_pg_model.get_connection_info()
    with psycopg.Connection.connect(**connection_info) as con, con.cursor() as cur:
        demo_pg_model.set_demo_searchpath(cur)
        sapi.insert_into_tree(cur, tree_dict)
    