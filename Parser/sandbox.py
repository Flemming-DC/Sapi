from __future__ import annotations
# import yaml
import json
import psycopg
# from dataclasses import dataclass
from pydantic import BaseModel
import sapi
from test import demo_pg_model, runtime_model

class Tab0_(BaseModel):
    col0_1_: str
    col0_2_: str
    shc_: str
class Tab1_(BaseModel):
    col1_1_: str
    col1_2_: str
    shc_: str
class Sht__(BaseModel):
    tab_id: int
    col_1__: str
    col_2__: str
class Tab_(BaseModel): # model for the little tree (tab_, tab0_, tab1_, sht__)
    # tab_ (tab__id,  col_1_,  col_2_)                  
    # tab0_(tab0__id, tab__id, col0_1_, col0_2_, shc_) 
    # tab1_(tab1__id, tab__id, col1_1_, col1_2_, shc_) 
    # sht__(sht___id, tab_id,  tab__id, col_1__, col_2__) 
    col_1_: str
    col_2_: str
    tab0_: list[Tab0_]
    tab1_: list[Tab1_]
    sht__: list[Sht__]

def insert_function() -> dict:
    with open('tree_.json') as f:
        tree_dict: dict = json.load(f)
    data_model = runtime_model.make_datamodel()

    connection_info = demo_pg_model.get_connection_info()
    with psycopg.Connection.connect(**connection_info) as con, con.cursor() as cur:
        cur.execute("set search_path to sapi_demo")
        sapi.insert_into_tree(cur, "tab_", tree_dict)
    
    # sapi.insert_into_tree("tree_", tree_dict, data_model)


def insert_query():
    with open('tree_.json') as f:
        tree_dict: dict = json.load(f)
    tree_ = Tab_(**tree_dict)
    tree_json = tree_.model_dump_json()
    sapi_query = f"""
        insert into tree
        values ({tree_json})
        """
    # big_sapi_query = f"""
    #     WITH cte AS (
    #         SELECT col0_1, col0_2, col00_2 FROM tree
    #     )
    #     insert into tree
    #     select {tree_json}
    #     from cte
    #     """
    hyp_expected_sql = """
insert into tab_ (col_1_, col_2_) values ('from json', 'from json') returning tab__id;

insert into tab0_ (tab__id, col0_1_, col0_2_, shc_)     values (tab__id, 'from json', 'from json', 'from json') returning tab0__id;
insert into tab1_ (tab__id, col1_1_, col1_2_, shc_)     values (tab__id, 'from json', 'from json', 'from json') returning tab1__id;
insert into sht__ (tab__id, tab_id, col1_1__, col_2__)  values (tab__id,           1, 'from json', 'from json') returning sht___id;
"""
    # the syntax for "returning id" is dialect dependent. In some dialects it is a seperate command. 
    expected_plpgsql = """
DO $$
DECLARE tab__id bigint;
BEGIN
    insert into tab_  (col_1_, col_2_) values ('from json', 'from json') returning tab__id;
    insert into tab0_ (tab__id, col0_1_, col0_2_, shc_)     values (tab__id, 'from json', 'from json', 'from json'); -- returning tab0__id;
    insert into tab1_ (tab__id, col1_1_, col1_2_, shc_)     values (tab__id, 'from json', 'from json', 'from json'); -- returning tab1__id;
    insert into sht__ (tab__id, tab_id, col1_1__, col_2__)  values (tab__id,           1, 'from json', 'from json'); -- returning sht___id;
END$$;
"""

    data_model = runtime_model.make_datamodel()
    sql = sapi.parse(sapi_query, data_model, str)
    
    print("--- sql-str ---")
    print(sql)

    connection_info = demo_pg_model.get_connection_info()
    with psycopg.Connection.connect(**connection_info) as con, con.cursor() as cur:
        cur.execute("set search_path to sapi_demo")
        data = cur.execute(sql).fetchall()
        print("--- low_level ---")
        print(data)



if __name__ == '__main__':
    insert_function()
    

