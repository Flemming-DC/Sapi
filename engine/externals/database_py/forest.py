from __future__ import annotations
from dataclasses import dataclass
from anytree import Node
from textwrap import dedent

from psycopg import Connection, Cursor # suspect
from psycopg.rows import dict_row, DictRow # this only allows access by name, not index :(
from . import database_deployment
from dataclasses import dataclass
from typing import Callable
from . import dialect



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


class Forest:
    _current: Forest|None = None
    # forest = Forest.from_datebase(connection_info, dialect)
    # trees = _load_trees_from_db(connection_info, dialect)

    def __init__(_, trees: list[Tree]):
        _._table_tree_names: list[str] = []
        _._trees_by_table: dict[str, list[str]] = {}
        _._tables_by_var: dict[str, list[str]]  = {}
        _._tables_by_var_and_tree: dict[tuple[str, str], list[str]] = {}
        _._node_by_tab_and_tree: dict[tuple[str, str], Node] = {}
        _._all_tables: list[str] = []

        for tree in trees:
            if tree.name in _._table_tree_names:
                raise Exception(f"You cannot have two trees with the same name. name = {tree.name}")
            _._table_tree_names.append(tree.name)
            for tab in tree.tables:
                if tab.name not in _._all_tables:
                    _._all_tables.append(tab.name)
                
                if tab.name not in _._trees_by_table.keys():
                    _._trees_by_table[tab.name] = []
                if tree.name not in _._trees_by_table[tab.name]: 
                    _._trees_by_table[tab.name].append(tree.name)

                _._node_by_tab_and_tree[(tab.name, tree.name)] = Node(tab.name) # parent is set later

                for col in tab.columns:
                    if col not in _._tables_by_var.keys():
                        _._tables_by_var[col] = []
                    if tab.name not in _._tables_by_var[col]: 
                        _._tables_by_var[col].append(tab.name)

                    if (col, tree.name) not in _._tables_by_var_and_tree.keys():
                        _._tables_by_var_and_tree[(col, tree.name)] = []
                    if tab.name not in _._tables_by_var_and_tree[(col, tree.name)]: 
                        _._tables_by_var_and_tree[(col, tree.name)].append(tab.name)
                    
            for tab in tree.tables:
                node = _._node_by_tab_and_tree.get((tab.name, tree.name))
                parent_node = _._node_by_tab_and_tree.get((tab.parent, tree.name))
                if node and parent_node:
                    node.parent = parent_node


def _with_cursor(func: Callable):
    database_deployment.setup()
    with open('../sapi_secret/pg_password.txt') as f:
        password = f.read()
    with Connection.connect(host='localhost', port = 5432, dbname = 'postgres', user = 'postgres', password=password) as con:
        with con.cursor(row_factory=dict_row) as cur:
            cur.execute("set search_path to sapi_sys")
            func(cur)

def _make_trees(cur: Cursor[DictRow]):
    columns_query = dialect.columns_query[dialect.dialect_str]
    foreign_keys_query = dialect.foreign_keys_query[dialect.dialect_str]

    columns_data = cur.execute(f"""
        WITH columns as ({columns_query})
        SELECT 
            tree.schema_name,
            tree.tree_name,
            sapi_tables.table_name,
            col.column_name,
            sapi_tables.sapi_tables_id
        FROM sapi_sys.sapi_trees AS tree 
        JOIN sapi_sys.sapi_tables ON sapi_tables.sapi_trees_id = tree.sapi_trees_id
        LEFT JOIN columns AS col ON col.table_name = sapi_tables.table_name and col.schema_name = tree.schema_name
        ORDER BY tree.schema_name, tree.tree_name, sapi_tables.table_name, col.column_name
        """).fetchall()
    join_info = cur.execute(f"""
        WITH foreign_keys as ({foreign_keys_query})
        select 
            tab.sapi_tables_id,
            ref_tab.table_name as parent,
            fk.primary_key_col,
            fk.foreign_key_col 
        from sapi_sys.sapi_tables as tab
        join sapi_sys.sapi_tables as ref_tab using (sapi_trees_id)
        join sapi_sys.sapi_trees as trees using (sapi_trees_id)
        join foreign_keys as fk
            on trees.schema_name = fk.schema
            and trees.schema_name = fk.referenced_schema
            and tab.table_name = fk.table
            and ref_tab.table_name = fk.referenced_table
        """).fetchall()
    join_info_by_table_id = {j['sapi_tables_id']: j for j in join_info}

    trees: list[Tree] = []
    current_tree: Tree|None = None
    current_table: Table|None = None
    for col_row in columns_data:
        if not current_tree or col_row['tree_name'] != current_tree.name:
            current_tree = Tree(tables=[], name=col_row['tree_name'], schema=col_row['schema_name'])
            trees.append(current_tree)

        # now current_tree must exist
        if not current_table or col_row['table_name'] != current_table.name:
            current_table = Table(name=col_row['table_name'], parent=None, columns=[])
            if current_table.name in [t.name for t in current_tree.tables]:
                raise Exception("Table name should be unique inside tree.")
            current_tree.tables.append(current_table)
            # set parent and any necessary join info
            join_info = join_info_by_table_id.get(col_row['sapi_tables_id'], None)
            if join_info: # join_info is None for the root table
                current_table.parent = join_info['parent']

        # now current_table must exist
        if col_row['column_name'] is None:
            raise Exception(dedent(f"""
                Failed to find any schema {col_row['schema_name']} containing a tree {col_row['tree_name']} 
                containing a table {col_row['table_name']} containing any columns. 
                """))
        # now col_row['column_name'] must exist
        current_table.columns.append(col_row['column_name'])

    return trees


def set_current(forest: Forest): Forest._current = forest

# read from current forest
def table_tree_names():       return Forest._current._table_tree_names
def trees_by_table():         return Forest._current._trees_by_table
def tables_by_var():          return Forest._current._tables_by_var
def tables_by_var_and_tree(): return Forest._current._tables_by_var_and_tree
def node_by_tab_and_tree():   return Forest._current._node_by_tab_and_tree
def all_tables():             return Forest._current._all_tables



