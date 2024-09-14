"""
plan:
    * database -> Table, Tree (done, omg man)
    * Table, Tree -> InternalForest
    * test the code by plugging it into the hardcoded trees file
    * separate datamodel / externals from parsing.
    * support runtime forest by skipping all or some of the step (database -> Table, Tree) when data is provided explicitly
    * support safety by checking the validity of the trees in step (database -> Table, Tree)
    * support choice between runtime forest or database forest and choice of database
"""

from typing import Callable
from anytree import Node
from dataclasses import dataclass

@dataclass
class Table:
    name: str # by hand or from sapi_sys
    acronym: str # by hand or from sapi_sys
    join_rule: str # by hand or from sapi_sys, evt. cast to type list[token], code for joing on parent
    parent: str # by hand or from builtin metadata, evt. cast to Table 
    columns: list[str] # by hand or from builtin metadata

# does this even need to be a class?
@dataclass
class Tree: # by hand or from sapi_sys, evt. call it TableTree 
    tables: list[Table]
    # mayby a skema?
    # insertable: bool = True
    # deletable: bool = True

# does this even need to be a class?
@dataclass
class Forest: # evt. call it DataModel
    trees: list[Tree]
    dialect: str # or sqlGlot.Dialect or a custom made Dialect enum. Mayby cast enum to sqlGlot.Dialect
    connect: Callable # e.g. psycopg.connect

    # init call finish_tables

def _finish_tables(forest: Forest):
    # from dialect get dialect dependent queries for metadata.
    # fetch data from sapi system tables.
    # check that fk-data and sapi-data satisfies sapy's requirements and apply circle breaking if asked
    # fill out missing info in tables inside trees
    # process tables to build the Internal Forest 
    ...


def _read_sql_metadata(cursor, dialect):
    # columns query: (schema, table, column) 
    # can a (table, ref_table) have multiple foreign key col_combs?. I think so, but not inside a single tree. Only ref parent. 
    # forign key query: (schema, table, column_combination, referenced_schema, referenced_table, referenced_column_combination)
    # evt. no array agg in query. agg in python
    ...

def _read_sapi_metadata(cursor):
    # read sapi + sql columns query: (schema, tree, table, column)
    # evt. if agg columns and if receiving a comma seperated string, then cast to list
    # evt. agg in python
    # evt. build list of (schema, tree, table, columns, fk_cols, fk_referenced_cols)
    ...

def _build_internal_forest(trees: list[Tree]):
    ...

# cast fk-data into join str in the absence of join_overwrites (per table and after finding parent)
# cast join str into join tokens


@dataclass
class InternalForest:
    table_tree_names: list[str] # from sapi_sys or from Tree
    trees_by_table: dict[str, list[str]] # from sapi_sys or from Tree + Table
    tables_by_var: dict[str, list[str]] # from sapi_sys + columns query or from Table
    tables_by_var_and_tree: dict[tuple[str, str], list[str]] # from sapi_sys + columns query or from Tree + Table
    node_by_table: dict[str, Node] # from sapi_sys + foreign keys or from Table
    all_tables: list[str] # from sapi_sys or from Table
    # join_rule_by_table  # from sapi_sys + foreign keys or from Table

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
        self.node_by_table = _make_node_by_table(table_data, self.trees_by_table)
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

def _make_node_by_table(_table_data: list[TableData], trees_by_table: dict[str, list[str]]) -> dict[str, Node]:
    node_by_table: dict[str, Node] = {}
    for row in _table_data:
        trees_with_table = trees_by_table[row.table]
        for tree in trees_with_table:
            parents_in_tree = [parent for parent in row.refers_to if tree in trees_by_table[parent]] # fix upper case BS
            if len(parents_in_tree) > 1:
                raise Exception(f"table {row.table} has the parents {parents_in_tree} in the tree {tree}, "
                                "but multiple parents are not allowed.")
            parent = parents_in_tree[0] if parents_in_tree else None
            node_by_table[row.table] = Node(row.table, parent = node_by_table.get(parent))
    return node_by_table




