from anytree import Node

# only include data for tables and columns that belong to some tree
table_tree_names = ['TREE', 'tree']

# If a table belongs to multiple trees, then you cannot use it in a query that references both trees
trees_by_table = {
    'TAB':   ['TREE'],
    'TAB0':  ['TREE'],
    'TAB1':  ['TREE'],
    'TAB2':  ['TREE'],
    'TAB00': ['TREE'],
    'TAB01': ['TREE'],
    'TAB10': ['TREE'],
    'TAB20': ['TREE'],
    'TAB21': ['TREE'],
    'tab':   ['tree'],
    'tab0':  ['tree'],
    'tab1':  ['tree'],
}


# tab, parent, columns
_table_data = [
    {'table': 'TAB',   'parent':  None,  'columns': ['COL_1',   'COL_2']},
    {'table': 'TAB0',  'parent': 'TAB',  'columns': ['COL0_1',  'COL0_2']},
    {'table': 'TAB1',  'parent': 'TAB',  'columns': ['COL1_1',  'COL1_2']},
    {'table': 'TAB2',  'parent': 'TAB',  'columns': ['COL2_1',  'COL2_2']},
    {'table': 'TAB00', 'parent': 'TAB0', 'columns': ['COL00_1', 'COL00_2']},
    {'table': 'TAB01', 'parent': 'TAB0', 'columns': ['COL01_1', 'COL01_2']},
    {'table': 'TAB10', 'parent': 'TAB1', 'columns': ['COL10_1', 'COL10_2']},
    {'table': 'TAB20', 'parent': 'TAB2', 'columns': ['COL20_1', 'COL20_2']},
    {'table': 'TAB21', 'parent': 'TAB2', 'columns': ['COL21_1', 'COL21_2']},
    {'table': 'tab',   'parent':  None,  'columns': ['col_1',   'col_2']},
    {'table': 'tab0',  'parent': 'tab',  'columns': ['col0_1',  'col0_2']},
    {'table': 'tab1',  'parent': 'tab',  'columns': ['col1_1',  'col1_2']},
]

# error: two tables could contain columns with the same name
table_by_var = {}
for row in _table_data:
    for col in row['columns']:
        table_by_var[col] = row['table']

node_by_table = {}
for row in _table_data:
    node_by_table[row['table']] = Node(row['table'], parent = node_by_table.get(row['parent']))

all_tables = [t['table'] for t in _table_data]





