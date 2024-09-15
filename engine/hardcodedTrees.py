from data_model import DataModel, TableData

# only include data for tables and columns that belong to some tree
table_tree_names = ['tree', 'tree_']

# If a table belongs to multiple trees, then you cannot use it in a query that references both trees
trees_by_table = {
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
    'sht__': ['tree', 'tree_'],
}

# tab, references, columns (other than fk and pk)
_table_data = [
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
"""
tree = Tree(
    tables = [
        'tab', 
        ('tab0', 't0'), 
        ...
        ], 
    join_rules = {
        ('tab', 'tab0'): 'join_code',
        ...
        }
    )

tree = Tree(
    tables = [
        Table(name='tab'),
        Table(name='tab', acronym='t0', join_rule='join_with_parent_code'), 
        ...
        ], 
    )
# refers_to and columns will be read from database or provided by hand
data_model = DataModel(trees=[tree, ...])

# trees can also come from db via sapi_sys tables
3 what about this?
tree = Tree(
    tables = [
        Table(name='tab'),
        Table(name='tab', acronym='t0', join_rule='join_with_parent_code'), 
        ...
        ], 
    )
data_model = DataModel(database_connection, database_dialect, trees containing any info thats not in db)


"""

_table_data = [TableData(**td) for td in _table_data]
_data_model = DataModel(table_tree_names, trees_by_table, _table_data)


table_tree_names = _data_model.table_tree_names
trees_by_table = _data_model.trees_by_table
tables_by_var = _data_model.tables_by_var
tables_by_var_and_tree = _data_model.tables_by_var_and_tree
node_by_tab_and_tree = _data_model.node_by_tab_and_tree
all_tables = _data_model.all_tables

# error: node_by_table['sht__'] has ill-defined parent, since its parent is different in different trees

import step2
from anytree import Node


# print(1, set(table_tree_names) == set(step2.table_tree_names)) # True
# print(2, trees_by_table == step2.trees_by_table) # True
# print(3, tables_by_var == step2.tables_by_var)
# print(4, tables_by_var_and_tree == step2.tables_by_var_and_tree)
# print(5, node_by_tab_and_tree == step2.node_by_tab_and_tree)
# print(6, set(step2.all_tables) == set(all_tables)) # True

# print(7, tables_by_var.keys() == step2.tables_by_var.keys()) # True
# print(8, tables_by_var_and_tree.keys() == step2.tables_by_var_and_tree.keys()) # True
# print(9, node_by_tab_and_tree.keys() == step2.node_by_tab_and_tree.keys()) # True

# for var in tables_by_var.keys():
#     if set(tables_by_var[var]) != set(step2.tables_by_var[var]):
#         print(3, var, ": ", set(tables_by_var[var]), set(step2.tables_by_var[var])) # True
# for vt in tables_by_var_and_tree.keys():
#     if set(tables_by_var_and_tree[vt]) != set(step2.tables_by_var_and_tree[vt]):
#         print(4, vt, ": ", set(tables_by_var_and_tree[vt]) - set(step2.tables_by_var_and_tree[vt]), "   ", set(step2.tables_by_var_and_tree[vt]))
# for tt in node_by_tab_and_tree.keys():
#     def same(n1: Node, n2: Node):
#         if repr(n1) != repr(n2):
#             return False
#         if str(n1) != str(n2):
#             return False
#         if repr(n1.parent) != repr(n2.parent):
#             return False
#         return True
#     if not same(node_by_tab_and_tree[tt], step2.node_by_tab_and_tree[tt]):
#         print(5, tt, ": ", node_by_tab_and_tree[tt], step2.node_by_tab_and_tree[tt])

...
table_tree_names = step2.table_tree_names
trees_by_table = step2.trees_by_table
tables_by_var = step2.tables_by_var
tables_by_var_and_tree = step2.tables_by_var_and_tree
node_by_tab_and_tree = step2.node_by_tab_and_tree
all_tables = step2.all_tables




