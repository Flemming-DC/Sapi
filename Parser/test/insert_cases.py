import json
from collections import namedtuple

# -------- define cases -------- #
Case = namedtuple('Case', ['sapi', 'expected_sql'])

def _query(data: dict[list[dict]]): 
    json_data = json.dumps(data)
    # return f"insert into tree_ values ($${json_data}$$)" 
    return f"insert $${json_data}$$" 



case1 = Case( # empty string
    sapi = _query({'tab_': [{
        'col_1_': 'from json',
        'col_2_': 'from json',
        'tab0_': [{'col0_1_': 'from json', 'col0_2_': 'from json', 'shc_': 'from json'}],
        'tab1_': [{'col1_1_': 'from json', 'col1_2_': 'from json', 'shc_': 'from json'}],
        'sht__': [{'tab_id': 1, 'col_1__': 'from json', 'col_2__': 'from json'}],
        }]}),
    expected_sql = f"""
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
    """)

case2 = Case(
    sapi = _query({'tab': [{
        'col_1': 'from json',
        'col_2': 'from json',
        'tab0': [{'col0_1': 'from json', 'col0_2': 'from json', 'shc': 'from json'}],
        'tab1': [{'col1_1': 'from json', 'col1_2': 'from json', 'shc': 'from json'}],
        'sht__': [{'tab_id': 1, 'col_1__': 'from json', 'col_2__': 'from json'}],
        }]}),
    expected_sql = """
        insert into tab (col_1, col_2)
        select 'from json', 'from json'
        ;
        with parent as (select max(tab_id) as id from tab)
        insert into tab0 (tab_id, col0_1, col0_2, shc)
        select parent.id, 'from json', 'from json', 'from json' from parent
        ;
        with parent as (select max(tab_id) as id from tab)
        insert into tab1 (tab_id, col1_1, col1_2, shc)
        select parent.id, 'from json', 'from json', 'from json' from parent
        ;
        with parent as (select max(tab_id) as id from tab)
        insert into sht__ (tab_id, tab_id, col_1__, col_2__)
        select parent.id, 1, 'from json', 'from json' from parent
    """)

case3 = Case(
    sapi = _query({'tab': [{
        'col_1': 'from json',
        'col_2': 'from json',
        'tab0': [{
                'col0_1': 'from json', 
                'col0_2': 'from json', 
                'shc': 'from json',
                'tab00':[{'col00_1': 'from json', 'col00_2': 'from json'}],
            }],
        'tab1': [{'col1_1': 'from json', 'col1_2': 'from json', 'shc': 'from json'}],
        }]}),
    expected_sql = """
        insert into tab (col_1, col_2)
        select 'from json', 'from json'
        ;
        with parent as (select max(tab_id) as id from tab)
        insert into tab0 (tab_id, col0_1, col0_2, shc)
        select parent.id, 'from json', 'from json', 'from json' from parent
        ;
        with parent as (select max(tab0_id) as id from tab0)
        insert into tab00 (tab0_id, col00_1, col00_2)
        select parent.id, 'from json', 'from json' from parent
        ;
        with parent as (select max(tab_id) as id from tab)
        insert into tab1 (tab_id, col1_1, col1_2, shc)
        select parent.id, 'from json', 'from json', 'from json' from parent
    """)

case4 = Case(
    sapi = _query({'tab': [{
        'col_1': 'from json',
        'col_2': 'from json',
        'tab0': [{'col0_1': 'from json', 'col0_2': 'from json', 'shc': 'from json'}],
        'tab1': [
            {'col1_1': 'from json 1', 'col1_2': 'from json 1', 'shc': 'from json 1'},
            {'col1_1': 'from json 2', 'col1_2': 'from json 2', 'shc': 'from json 2'},
            {'col1_1': 'from json 3', 'col1_2': 'from json 3', 'shc': 'from json 3'},
            ],
        'sht__': [{'tab_id': 1, 'col_1__': 'from json', 'col_2__': 'from json'}],
        }]}),
    expected_sql = """
        insert into tab (col_1, col_2)
        select 'from json', 'from json'
        ;
        with parent as (select max(tab_id) as id from tab)
        insert into tab0 (tab_id, col0_1, col0_2, shc)
        select parent.id, 'from json', 'from json', 'from json' from parent
        ;
        with parent as (select max(tab_id) as id from tab)
        insert into tab1 (tab_id, col1_1, col1_2, shc)
        select parent.id, 'from json 1', 'from json 1', 'from json 1' from parent union
        select parent.id, 'from json 2', 'from json 2', 'from json 2' from parent union
        select parent.id, 'from json 3', 'from json 3', 'from json 3' from parent
        ;
        with parent as (select max(tab_id) as id from tab)
        insert into sht__ (tab_id, tab_id, col_1__, col_2__)
        select parent.id, 1, 'from json', 'from json' from parent
    """)

case5 = Case(
    sapi = _query({'tab0': [{
        'tab_id': 1,
        'col0_1': 'from json',
        'col0_2': 'from json',
        'tab01': [{'col01_1': 'from json', 'col01_2': 'from json'}],
        }]}),
    expected_sql = """
        insert into tab0 (tab_id, col0_1, col0_2)
        select 1, 'from json', 'from json'
        ;
        with parent as (select max(tab0_id) as id from tab0)
        insert into tab01 (tab0_id, col01_1, col01_2)
        select parent.id, 'from json', 'from json' from parent
    """)

def case_manual_pk(tab_manual_id: int, tab0_manual_id: int): return Case(
    sapi = _query({'tab_manual': [{
        'tab_manual_id': tab_manual_id,
        'col_manual_1': 'from json',
        'col_manual_2': 'from json',
        'tab0_manual': [{'tab0_manual_id': tab0_manual_id, 'col0_manual_1': 'from json', 'col0_manual_2': 'from json'}],
        }]}),
    expected_sql = f"""
        insert into tab_manual (tab_manual_id, col_manual_1, col_manual_2)
        select {tab_manual_id}, 'from json', 'from json'
        ;
        with parent as (select max(tab_manual_id) as id from tab_manual)
        insert into tab0_manual (tab_manual_id, tab0_manual_id, col0_manual_1, col0_manual_2)
        select parent.id, {tab0_manual_id}, 'from json', 'from json' from parent
        ;
    """)


# empty_case = Case(
#     sapi = _query({'': [{
#         }]}),
#     expected_sql = """
#     """)


insert_cases = [case1, case2, case3, case4, case5]
# insert_error_cases = [] 
# non_executable_insert = []
print(f"insert test cases = {len(insert_cases) + len([case_manual_pk])}")# + len(insert_error_cases) + len(non_executable_insert)}")


insert_cases = [case5] 
