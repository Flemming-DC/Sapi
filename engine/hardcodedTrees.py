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
    'TaB3':  ['TREE', 'tree'],
}

# tab, references, columns (other than fk and pk)
_table_data = [
    {'table': 'TAB',   'refers_to': [],              'columns': ['COL_1',   'COL_2']},
    {'table': 'TAB0',  'refers_to': ['TAB', 'tab1'], 'columns': ['COL0_1',  'COL0_2', 'SHARED']},
    {'table': 'TAB1',  'refers_to': ['TAB', 'tab0'], 'columns': ['COL1_1',  'COL1_2', 'SHARED']},
    {'table': 'TAB2',  'refers_to': ['TAB'],         'columns': ['COL2_1',  'COL2_2']},
    {'table': 'TAB00', 'refers_to': ['TAB0'],        'columns': ['COL00_1', 'COL00_2']},
    {'table': 'TAB01', 'refers_to': ['TAB0'],        'columns': ['COL01_1', 'COL01_2']},
    {'table': 'TAB10', 'refers_to': ['TAB1'],        'columns': ['COL10_1', 'COL10_2']},
    {'table': 'TAB20', 'refers_to': ['TAB2'],        'columns': ['COL20_1', 'COL20_2']},
    {'table': 'TAB21', 'refers_to': ['TAB2'],        'columns': ['COL21_1', 'COL21_2']},
    {'table': 'tab',   'refers_to': [],              'columns': ['col_1',   'col_2']},
    {'table': 'tab0',  'refers_to': ['tab', 'TAB1'], 'columns': ['col0_1',  'col0_2', 'shared']},
    {'table': 'tab1',  'refers_to': ['tab', 'TAB0'], 'columns': ['col1_1',  'col1_2', 'shared']},
    {'table': 'TaB3',  'refers_to': ['tab', 'TAB' ], 'columns': ['CoL4_1',  'CoL3_2']},
]

# # tab, parent, columns
# _table_data = [
#     {'table': 'TAB',   'parent':  None,  'columns': ['COL_1',   'COL_2']},
#     {'table': 'TAB0',  'parent': 'TAB',  'columns': ['COL0_1',  'COL0_2']},
#     {'table': 'TAB1',  'parent': 'TAB',  'columns': ['COL1_1',  'COL1_2']},
#     {'table': 'TAB2',  'parent': 'TAB',  'columns': ['COL2_1',  'COL2_2']},
#     {'table': 'TAB00', 'parent': 'TAB0', 'columns': ['COL00_1', 'COL00_2']},
#     {'table': 'TAB01', 'parent': 'TAB0', 'columns': ['COL01_1', 'COL01_2']},
#     {'table': 'TAB10', 'parent': 'TAB1', 'columns': ['COL10_1', 'COL10_2']},
#     {'table': 'TAB20', 'parent': 'TAB2', 'columns': ['COL20_1', 'COL20_2']},
#     {'table': 'TAB21', 'parent': 'TAB2', 'columns': ['COL21_1', 'COL21_2']},
#     {'table': 'tab',   'parent':  None,  'columns': ['col_1',   'col_2']},
#     {'table': 'tab0',  'parent': 'tab',  'columns': ['col0_1',  'col0_2']},
#     {'table': 'tab1',  'parent': 'tab',  'columns': ['col1_1',  'col1_2']},
# ]

# error: two tables could contain columns with the same name
table_by_var = {}
for row in _table_data:
    for col in row['columns']:
        table_by_var[col] = row['table']

node_by_table = {}
for row in _table_data:
    trees_with_table = trees_by_table[row['table']]
    for tree in trees_with_table:
        parents_in_tree = [parent for parent in row['refers_to'] if tree in trees_by_table[parent]]
        if len(parents_in_tree) > 1:
            raise Exception(f"Table {row['table']} has the parents {parents_in_tree} in the tree {tree}, "
                            "but multiple parents are not allowed.")
        parent = parents_in_tree[0] if parents_in_tree else None
        node_by_table[row['table']] = Node(row['table'], parent = node_by_table.get(parent))
        


    # trees_with_parent_table = [trees_by_table[parent] for parent in row['refers_to']]
    # # make a node for each tree that contains both the table and a parent
    # for tree in trees_with_table:
    #     if tree not in trees_with_parent_table:
    #         continue
    #     node_by_table[row['table']] = Node(row['table'], parent = node_by_table.get(row['refers_to']))

all_tables = [t['table'] for t in _table_data]





