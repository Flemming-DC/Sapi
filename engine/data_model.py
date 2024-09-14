from anytree import Node
from dataclasses import dataclass

@dataclass
class TableData: # temporary data structure
    table: str # table name
    refers_to: list[str] # list of foreign key table names. Evt. support unchecked references too
    columns: list[str] # list of column names


class DataModel:

    def __init__(self, table_tree_names: list[str], trees_by_table: dict[str, list[str]], table_data: list[TableData]):
        self.table_tree_names = table_tree_names
        self.trees_by_table = trees_by_table
        self.tables_by_var = _make_tables_by_var(table_data)
        self.tables_by_var_and_tree = _make_tables_by_var_and_tree(table_tree_names, trees_by_table, self.tables_by_var)
        self.node_by_tab_and_tree = _make_node_by_tab_and_tree(table_data, self.trees_by_table)
        self.all_tables: list[str] = [t.table for t in table_data]



def _make_tables_by_var(table_data: list[TableData]) -> dict[str, list[str]]:
    tables_by_var: dict[str, list[str]] = {}
    for row in table_data:
        for col in row.columns:
            if col not in tables_by_var.keys():
                tables_by_var[col] = []
            tables_by_var[col].append(row.table)
    return tables_by_var

def _make_tables_by_var_and_tree(
        table_tree_names: list[str], trees_by_table: dict[str, list[str]], tables_by_var: dict[str, list[str]]
        ) -> dict[tuple[str, str], list[str]]:
    tables_by_var_and_tree: dict[tuple[str, str], list[str]] = {}
    for var, tabs_of_var in tables_by_var.items():
        for tree in table_tree_names:
            tabs_of_var_in_tree = [tab for tab in tabs_of_var if tree in trees_by_table[tab]]
            tables_by_var_and_tree[(var, tree)] = tabs_of_var_in_tree
    return tables_by_var_and_tree

def _make_node_by_tab_and_tree(_table_data: list[TableData], trees_by_table: dict[str, list[str]]) -> dict[tuple[str, str], Node]:
    node_by_tab_and_tree: dict[str, Node] = {}
    for row in _table_data:
        trees_with_table = trees_by_table[row.table]
        for tree in trees_with_table:
            parents_in_tree = [parent for parent in row.refers_to if tree in trees_by_table[parent]] # fix upper case BS
            if len(parents_in_tree) > 1:
                raise Exception(f"table {row.table} has the parents {parents_in_tree} in the tree {tree}, "
                                "but multiple parents are not allowed.")
            parent = parents_in_tree[0] if parents_in_tree else None
            node_by_tab_and_tree[(row.table, tree)] = Node(row.table, parent = node_by_tab_and_tree.get((parent, tree)))
    return node_by_tab_and_tree




