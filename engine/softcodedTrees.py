from anytree import Node
from psycopg import Connection
from psycopg.rows import dict_row # this only allows access by name, not index :(
import database_deployment
# only include data for tables and columns that belong to some tree

database_deployment.setup()

def fetch_data_from_postgres():
    with open('../sapi_secret/pg_password.txt') as f:
        password = f.read()
    with Connection.connect(host='localhost', port = 5432, dbname = 'postgres', user = 'postgres', password=password) as con:
        with con.cursor(row_factory=dict_row) as cur:
            cur.execute("set search_path to sapi_sys")

            table_tree_names_ = cur.execute("select tree_name from sapi_trees").fetchall()
            table_tree_names_: list[str] = [row['tree_name'] for row in table_tree_names_] # to column
            
            trees_by_table_ = cur.execute("""
                select 
                    table_name, 
                    array_agg(tree_name) as tree_names 
                from sapi_trees
                join sapi_tables using (sapi_trees_id)	
                group by table_name
                """).fetchall()
            trees_by_table_: dict[str, list[str]] = {
                row['table_name']: row['tree_names'] for row in trees_by_table_} # to dict

            _columns = cur.execute("""
                SELECT
                    table_name as table,
                    array_agg(column_name::text) as columns
                FROM information_schema.columns
                where table_schema = 'sapi_demo'
                group by table_name
                    """).fetchall()
            _columns_by_table: dict[str, list[str]] = {
                row['table']: row['columns'] for row in _columns} # to dict

            # restrict references by schema
            _references_ = cur.execute("""
                SELECT
                    tab.relname             AS table, 
                    array_agg(ftab.relname) AS referenced_tables, 
                    -- array_agg(col.attname)    AS primary_key,
                    -- array_agg(fcol.attname)   AS foreign_key,
                    null
                FROM pg_constraint AS con
                JOIN pg_class      AS tab  ON tab.oid = con.conrelid
                JOIN pg_attribute  AS col  ON col.attnum = ANY(con.conkey) AND col.attrelid = con.conrelid
                JOIN pg_class      AS ftab ON ftab.oid = con.confrelid
                JOIN pg_attribute  AS fcol ON fcol.attnum = ANY(con.confkey) AND fcol.attrelid = con.confrelid
                WHERE con.contype = 'f'
                group by tab.relname
                """).fetchall()
            referenced_table_dict = {row['table']: row['referenced_tables'] for row in _references_} # to dict
            
            # init _table_data_ for the tables that are in some tree
            _table_data_: list[dict[str, str|list[str]]] = [
                {'table': table, 'refers_to': [], 'columns': []} for table in trees_by_table_.keys()]
            _table_data_.sort(key=lambda row: row['table'].lower())
            for i, row in enumerate(_table_data_):
                _table_data_[i]['columns'] = _columns_by_table[row['table'].lower()]
                _table_data_[i]['refers_to'] = referenced_table_dict.get(row['table'].lower(), [])

    return table_tree_names_, trees_by_table_, _table_data_


table_tree_names, trees_by_table, _table_data = fetch_data_from_postgres()

def test_fetch_data_from_postgres():
    _expected_table_tree_names = ['tree', 'tree_']

    # If a table belongs to multiple trees, then you cannot use it in a query that references both trees
    _expected_trees_by_table = {
        'tab':   ['tree'],
        'tab0':  ['tree'],
        'tab1':  ['tree'],
        'tab2':  ['tree'],
        'tab00': ['tree'],
        'tab01': ['tree'],
        'tab10': ['tree'],
        'tab20': ['tree'],
        'tab21': ['tree'],
        'tab_':  ['tree_'],
        'tab0_': ['tree_'],
        'tab1_': ['tree_'],
        'sht__':  ['tree', 'tree_'],
    }

    # tab, references, columns (other than fk and pk)
    _expected_table_data = [
        {'table': 'tab',   'refers_to': [],               'columns': ['tab_id',                         'col_1',   'col_2']},
        {'table': 'tab0',  'refers_to': ['tab', 'tab1_'], 'columns': ['tab0_id',  'tab_id', 'tab1__id', 'col0_1',  'col0_2', 'shc']},
        {'table': 'tab1',  'refers_to': ['tab', 'tab0_'], 'columns': ['tab1_id',  'tab_id', 'tab0__id', 'col1_1',  'col1_2', 'shc']},
        {'table': 'tab2',  'refers_to': ['tab'],          'columns': ['tab2_id',  'tab_id',             'col2_1',  'col2_2']},
        {'table': 'tab00', 'refers_to': ['tab0'],         'columns': ['tab00_id', 'tab0_id',            'col00_1', 'col00_2']},
        {'table': 'tab01', 'refers_to': ['tab0'],         'columns': ['tab01_id', 'tab0_id',            'col01_1', 'col01_2']},
        {'table': 'tab10', 'refers_to': ['tab1'],         'columns': ['tab10_id', 'tab1_id',            'col10_1', 'col10_2']},
        {'table': 'tab20', 'refers_to': ['tab2'],         'columns': ['tab20_id', 'tab2_id',            'col20_1', 'col20_2']},
        {'table': 'tab21', 'refers_to': ['tab2'],         'columns': ['tab21_id', 'tab2_id',            'col21_1', 'col21_2']},
        {'table': 'tab_',  'refers_to': [],               'columns': ['tab__id',                        'col_1_',  'col_2_']},
        {'table': 'tab0_', 'refers_to': ['tab_', 'tab1'], 'columns': ['tab0__id', 'tab__id', 'tab1_id', 'col0_1_', 'col0_2_', 'shc_']},
        {'table': 'tab1_', 'refers_to': ['tab_', 'tab0'], 'columns': ['tab1__id', 'tab__id', 'tab0_id', 'col1_1_', 'col1_2_', 'shc_']},
        {'table': 'sht__', 'refers_to': ['tab_', 'tab' ], 'columns': ['sht___id', 'tab__id', 'tab_id' , 'col_1__', 'col_2__']},
    ]
    _expected_table_data.sort(key=lambda row: row['table'].lower())

    assert table_tree_names == _expected_table_tree_names, ""
    assert trees_by_table == _expected_trees_by_table, ""
    assert len(_table_data) == len(_expected_table_data), ""
    for row, expected_row in zip(_table_data, _expected_table_data):
        print('--- row ---')
        print('actual:  ', row)
        print('expected:', expected_row)

        assert row['refers_to'] is not None, ""
        row['refers_to'] = set(row['refers_to'])
        row['columns'] = set(row['columns'])
        expected_row['refers_to'] = set(expected_row['refers_to'])
        expected_row['columns'] = set(expected_row['columns'])
        assert row == expected_row, ""

test_fetch_data_from_postgres()
print("asserts passed")


tables_by_var: dict[str, list[str]] = {}
for row in _table_data:
    for col in row['columns']:
        if col not in tables_by_var.keys():
            tables_by_var[col] = []
        tables_by_var[col].append(row['table'])

tables_by_var_and_tree = {}
for var, tabs_of_var in tables_by_var.items():
    for tree in table_tree_names:
        tabs_of_var_in_tree = [tab for tab in tabs_of_var if tree in trees_by_table[tab]]
        tables_by_var_and_tree[(var, tree)] = tabs_of_var_in_tree


node_by_table: dict[str, Node] = {}
for row in _table_data:
    trees_with_table = trees_by_table[row['table']]
    for tree in trees_with_table:
        parents_in_tree = [parent for parent in row['refers_to'] if tree in trees_by_table[parent]] # fix upper case BS
        if len(parents_in_tree) > 1:
            raise Exception(f"table {row['table']} has the parents {parents_in_tree} in the tree {tree}, "
                            "but multiple parents are not allowed.")
        parent = parents_in_tree[0] if parents_in_tree else None
        node_by_table[row['table']] = Node(row['table'], parent = node_by_table.get(parent))
        


all_tables: list[str] = [t['table'] for t in _table_data]





