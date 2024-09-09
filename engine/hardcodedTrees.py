from anytree import Node

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
    {'table': 'tab',   'refers_to': [],               'columns': ['col_1',   'col_2']},
    {'table': 'tab0',  'refers_to': ['tab', 'tab1_'], 'columns': ['col0_1',  'col0_2', 'SHC']},
    {'table': 'tab1',  'refers_to': ['tab', 'tab0_'], 'columns': ['col1_1',  'col1_2', 'SHC']},
    {'table': 'tab2',  'refers_to': ['tab'],          'columns': ['col2_1',  'col2_2']},
    {'table': 'tab00', 'refers_to': ['tab0'],         'columns': ['col00_1', 'col00_2']},
    {'table': 'tab01', 'refers_to': ['tab0'],         'columns': ['col01_1', 'col01_2']},
    {'table': 'tab10', 'refers_to': ['tab1'],         'columns': ['col10_1', 'col10_2']},
    {'table': 'tab20', 'refers_to': ['tab2'],         'columns': ['col20_1', 'col20_2']},
    {'table': 'tab21', 'refers_to': ['tab2'],         'columns': ['col21_1', 'col21_2']},
    {'table': 'tab_',  'refers_to': [],               'columns': ['col_1_',  'col_2_']},
    {'table': 'tab0_', 'refers_to': ['tab_', 'tab1'], 'columns': ['col0_1_', 'col0_2_', 'shc_']},
    {'table': 'tab1_', 'refers_to': ['tab_', 'tab0'], 'columns': ['col1_1_', 'col1_2_', 'shc_']},
    {'table': 'sht__', 'refers_to': ['tab_', 'tab' ], 'columns': ['col_1__', 'col_2__']},
]


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
            raise Exception(f"table {row['table']} has the parents {parents_in_tree} in the tree {tree}, "
                            "but multiple parents are not allowed.")
        parent = parents_in_tree[0] if parents_in_tree else None
        node_by_table[row['table']] = Node(row['table'], parent = node_by_table.get(parent))
        


all_tables = [t['table'] for t in _table_data]





