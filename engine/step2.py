from dataclasses import dataclass
from anytree import Node


@dataclass
class Table:
    name: str # by hand or from sapi_sys
    # acronym: str # by hand or from sapi_sys
    # join_rule: str # by hand or from sapi_sys, evt. cast to type list[token], code for joing on parent
    parent: str # by hand or from builtin metadata, evt. cast to Table 
    columns: list[str] # by hand or from builtin metadata
    # tree: 'Tree'

# does this even need to be a class?
@dataclass
class Tree: # by hand or from sapi_sys, evt. call it TableTree 
    tables: list[Table]
    name: str
    schema: str
    # insertable: bool = True
    # deletable: bool = True

@dataclass
class InternalForest:
    table_tree_names: list[str] # from sapi_sys or from Tree
    trees_by_table: dict[str, list[str]] # from sapi_sys or from Tree + Table
    tables_by_var: dict[str, list[str]] # from sapi_sys + columns query or from Table
    tables_by_var_and_tree: dict[tuple[str, str], list[str]] # from sapi_sys + columns query or from Tree + Table
    node_by_table: dict[str, Node] # from sapi_sys + foreign keys or from Table
    all_tables: list[str] # from sapi_sys or from Table
    # join_rule_by_table  # from sapi_sys + foreign keys or from Table

# this is output of step1
_tree = Tree(tables=[Table(name='sht__', parent='tab', columns=['col_1__', 'col_2__', 'sht___id', 'tab__id', 'tab_id']), Table(name='tab', parent=None, columns=['col_1', 'col_2', 'tab_id']), Table(name='tab0', parent='tab', columns=['col0_1', 'col0_2', 'shc', 'tab0_id', 'tab1__id', 'tab_id']), Table(name='tab00', parent='tab0', columns=['col00_1', 'col00_2', 'tab00_id', 'tab0_id']), Table(name='tab01', parent='tab0', columns=['col01_1', 'col01_2', 'tab01_id', 'tab0_id']), Table(name='tab1', parent='tab', columns=['col1_1', 'col1_2', 'shc', 'tab0__id', 'tab1_id', 'tab_id']), Table(name='tab10', parent='tab1', columns=['col10_1', 'col10_2', 'tab10_id', 'tab1_id']), Table(name='tab2', parent='tab', columns=['col2_1', 'col2_2', 'tab2_id', 'tab_id']), Table(name='tab20', parent='tab2', columns=['col20_1', 'col20_2', 'tab20_id', 'tab2_id']), Table(name='tab21', parent='tab2', columns=['col21_1', 'col21_2', 'tab21_id', 'tab2_id'])], 
            name='tree', schema='sapi_demo')
_tree_ = Tree(tables=[Table(name='sht__', parent='tab_', columns=['col_1__', 'col_2__', 'sht___id', 'tab__id', 'tab_id']), Table(name='tab_', parent=None, columns=['col_1_', 'col_2_', 'tab__id']), Table(name='tab0_', parent='tab_', columns=['col0_1_', 'col0_2_', 'shc_', 'tab0__id', 'tab1_id', 'tab__id']), Table(name='tab1_', parent='tab_', columns=['col1_1_', 'col1_2_', 'shc_', 'tab0_id', 'tab1__id', 'tab__id'])], 
             name='tree_', schema='sapi_demo')
trees = [_tree, _tree_]

# ----------- from trees to InternalForest ------------- #

table_tree_names: list[str] = []
trees_by_table: dict[str, list[str]] = {}
tables_by_var: dict[str, list[str]]  = {}
tables_by_var_and_tree: dict[tuple[str, str], list[str]] = {}
node_by_tab_and_tree: dict[tuple[str, str], Node] = {}
all_tables: list[str] = []


for tree in trees:
    table_tree_names.append(tree.name)
    for tab in tree.tables:
        if tab.name not in all_tables:
            all_tables.append(tab.name)
        
        if tab.name not in trees_by_table.keys():
            trees_by_table[tab.name] = []
        trees_by_table[tab.name].append(tree.name)

        node_by_tab_and_tree[(tab.name, tree.name)] = Node(tab.name) # parent is set later

        for col in tab.columns:
            if col not in tables_by_var.keys():
                tables_by_var[col] = []
            tables_by_var[col].append(tab.name)

            if col not in tables_by_var_and_tree.keys():
                tables_by_var_and_tree[(col, tree.name)] = []
            tables_by_var_and_tree[(col, tree.name)].append(tab.name)
            

    for tab in tree.tables:
        node = node_by_tab_and_tree.get((tab.name, tree.name))
        parent_node = node_by_tab_and_tree.get((tab.parent, tree.name))
        if node and parent_node:
            node.parent = parent_node

# root = node_by_tab_and_tree[('tab', _tree.name)]
# root_ = node_by_tab_and_tree[('tab_', _tree_.name)]
# from anytree import RenderTree
# print(RenderTree(root))
# print(RenderTree(root_))


# error: node_by_table is ill-defined, since node is tree dependent

