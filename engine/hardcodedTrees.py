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
    'shT3':  ['TREE', 'tree'],
}

# tab, references, columns (other than fk and pk)
_table_data = [
    {'table': 'TAB',   'refers_to': [],              'columns': ['COL_1',   'COL_2']},
    {'table': 'TAB0',  'refers_to': ['TAB', 'tab1'], 'columns': ['COL0_1',  'COL0_2', 'SHC']},
    {'table': 'TAB1',  'refers_to': ['TAB', 'tab0'], 'columns': ['COL1_1',  'COL1_2', 'SHC']},
    {'table': 'TAB2',  'refers_to': ['TAB'],         'columns': ['COL2_1',  'COL2_2']},
    {'table': 'TAB00', 'refers_to': ['TAB0'],        'columns': ['COL00_1', 'COL00_2']},
    {'table': 'TAB01', 'refers_to': ['TAB0'],        'columns': ['COL01_1', 'COL01_2']},
    {'table': 'TAB10', 'refers_to': ['TAB1'],        'columns': ['COL10_1', 'COL10_2']},
    {'table': 'TAB20', 'refers_to': ['TAB2'],        'columns': ['COL20_1', 'COL20_2']},
    {'table': 'TAB21', 'refers_to': ['TAB2'],        'columns': ['COL21_1', 'COL21_2']},
    {'table': 'tab',   'refers_to': [],              'columns': ['col_1',   'col_2']},
    {'table': 'tab0',  'refers_to': ['tab', 'TAB1'], 'columns': ['col0_1',  'col0_2', 'shc']},
    {'table': 'tab1',  'refers_to': ['tab', 'TAB0'], 'columns': ['col1_1',  'col1_2', 'shc']},
    {'table': 'shT3',  'refers_to': ['tab', 'TAB' ], 'columns': ['CoL4_1',  'CoL3_2']},
]


# error: two tables could contain columns with the same name
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

        # if len(tabs_of_var_in_tree) > 1:
        #     raise Exception(f"The tree '{tree}' contains multiple tables {tabs_of_var_in_tree} with column {var}.")
        # if len(tabs_of_var_in_tree) == 0:
        #     continue
        # # elif len(tabs_of_var_in_tree) == 0:
        #     raise Exception(f"The tree '{tree}' does not contain any table with column {var}.")
        # tab = tabs_of_var_in_tree[0]
        tables_by_var_and_tree[(var, tree)] = tabs_of_var_in_tree


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
        


all_tables = [t['table'] for t in _table_data]





