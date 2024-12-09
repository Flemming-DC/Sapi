from __future__ import annotations
from dataclasses import dataclass
from anytree import Node
from . import deployment
from .dialect import Dialect
from .pep249_database_api_spec_v2 import Cursor
from sapi._internals.error import CompilerError, DataModelError

@dataclass
class Table:
    name: str 
    parent: str 
    columns: list[str] 
    join_clause: str 
    # foreign_keys: str # a comma seperated list of foreign_keys

@dataclass
class Tree: # evt. call it TableTree 
    tables: list[Table]
    name: str
    schema: str
    # insertable: bool = True
    # deletable: bool = True


class DataModel:
    _current: DataModel|None = None

    def __init__(_, dialect: Dialect, trees: list[Tree]):
        _._table_tree_names: list[str] = []
        _._trees_by_table: dict[str, list[str]] = {}
        _._tables_by_var: dict[str, list[str]]  = {}
        _._tables_by_var_and_tree: dict[tuple[str, str], list[str]] = {}
        _._node_by_tab_and_tree: dict[tuple[str, str], Node] = {}
        _._join_clause_by_tab: dict[tuple[str, bool], str] = {}
        _._all_tables: list[str] = []
        _._dialect = dialect # used due to get sqlglot_dialect and black_from_clause

        for tree in trees:
            if tree.name in _._table_tree_names:
                raise DataModelError(f"You cannot have two trees with the same name in the same instance"
                                f" of the DataModel class. name = {tree.name}")
            _._table_tree_names.append(tree.name)
            for tab in tree.tables:
                if tab.name not in _._all_tables:
                    _._all_tables.append(tab.name)
                
                if tab.name not in _._trees_by_table.keys():
                    _._trees_by_table[tab.name] = []
                if tree.name not in _._trees_by_table[tab.name]: 
                    _._trees_by_table[tab.name].append(tree.name)

                if tab.name not in _._join_clause_by_tab.keys(): 
                    _._join_clause_by_tab[(tab.name, True)] = tab.join_clause # from child join parent
                    if tab.parent and not tab.join_clause: raise CompilerError(
                        "Table should have parent without having a rule for how to on join the parent")
                    if tab.parent:
                        _._join_clause_by_tab[(tab.name, False)] = tab.join_clause.replace(tab.parent, tab.name, 1) # from parent join child

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



    @staticmethod
    def from_database(dialect: Dialect, cur: Cursor, sys_schema: str) -> DataModel:
        cur.execute("savepoint DataModel_from_database")
        if not deployment.is_deployed(cur, dialect, sys_schema):
            raise DataModelError("You must call deployment.setup, before calling this function.")
        cur.execute(f"set search_path to {sys_schema}")
        trees = _make_trees(dialect, cur, sys_schema)
        cur.execute("rollback to savepoint DataModel_from_database")
        
        return DataModel(dialect, trees)


def _make_trees(dialect: Dialect, cur: Cursor, sys_schema: str) -> list[Tree]:
    columns_query = dialect.columns_query
    foreign_keys_query = dialect.foreign_keys_query

    cur.execute(f"""
        WITH columns as ({columns_query})
        SELECT 
            tree.schema_name,
            tree.tree_name,
            sapi_tables.table_name,
            col.column_name,
            sapi_tables.sapi_tables_id
        FROM {sys_schema}.sapi_trees AS tree 
        JOIN {sys_schema}.sapi_tables ON sapi_tables.sapi_trees_id = tree.sapi_trees_id
        LEFT JOIN columns AS col ON col.table_name = sapi_tables.table_name and col.schema_name = tree.schema_name
        ORDER BY tree.schema_name, tree.tree_name, sapi_tables.table_name, col.column_name
        """)
    columns_data = cur.fetchall()
    
    cur.execute(f"""
        WITH foreign_keys as ({foreign_keys_query})
        select 
            tab.sapi_tables_id,
            ref_tab.table_name as parent,
            fk.primary_key_col,
            fk.foreign_key_col,
            tab.join_clause 
        from {sys_schema}.sapi_tables as tab
        join {sys_schema}.sapi_tables as ref_tab using (sapi_trees_id)
        join {sys_schema}.sapi_trees as trees using (sapi_trees_id)
        join foreign_keys as fk
            on  trees.schema_name = fk.schema
            and trees.schema_name = fk.referenced_schema
            and tab.table_name = fk.table
            and ref_tab.table_name = fk.referenced_table
        """)
    join_info = cur.fetchall()
    join_info_by_table_id = {
        j[0]: {'parent': j[1], 'primary_key_col': j[2], 'foreign_key_col': j[3], 'join_clause': j[4]} 
        for j in join_info}

    cur.execute(f"""
        select distinct schema_name, table_name
        from {sys_schema}.sapi_tables
        join {sys_schema}.sapi_trees using (sapi_trees_id)
        """) 
    remaining_expected_tables = [schema + '.' + tab for schema, tab in cur.fetchall()] # used for error checking 

    trees: list[Tree] = []
    current_tree: Tree|None = None
    current_table: Table|None = None
    for col_row in columns_data:
        col_row = {
            'schema_name': col_row[0],
            'tree_name': col_row[1],
            'table_name': col_row[2],
            'column_name': col_row[3],
            'sapi_tables_id': col_row[4]}
        if not current_tree or col_row['tree_name'] != current_tree.name:
            current_tree = Tree(tables=[], name=col_row['tree_name'], schema=col_row['schema_name'])
            trees.append(current_tree)

        # now current_tree must exist
        if not current_table or col_row['table_name'] != current_table.name:
            current_table = Table(name=col_row['table_name'], parent=None, columns=[], join_clause=None)
            if current_table.name in [t.name for t in current_tree.tables]:
                raise DataModelError("Table name should be unique inside tree.")
            current_tree.tables.append(current_table)
            # set parent and any necessary join info
            join_info = join_info_by_table_id.get(col_row['sapi_tables_id'], None)
            if join_info: # join_info is None for the root table
                current_table.parent = join_info['parent']
                current_table.join_clause = str(join_info['join_clause']
                    ).replace('__parent__', join_info['parent']
                    ).replace('__keys__', join_info['foreign_key_col'])

            qualified_table = current_tree.schema + '.' + current_table.name
            if qualified_table in remaining_expected_tables:
                remaining_expected_tables.remove(qualified_table)

        # now current_table must exist
        if col_row['column_name'] is None:
            full_name = f"{col_row['schema_name']}.{col_row['tree_name']}.{col_row['table_name']}"
            raise DataModelError(f"Failed to find any table '{full_name}' containing any columns.")
        # now col_row['column_name'] must exist
        current_table.columns.append(col_row['column_name'])

    if remaining_expected_tables:
        raise DataModelError(f"Failed to find the following table even though they are listed in "
                            f"{sys_schema}.sapi_tables.\n{remaining_expected_tables}")

    return trees


def set_current(dataModel: DataModel): DataModel._current = dataModel

# read from current dataModel
def is_var(tok_text: str):   return tok_text in DataModel._current._tables_by_var.keys()
def is_tree(tok_text: str):  return tok_text in DataModel._current._table_tree_names
def is_table(tok_text: str): return tok_text in DataModel._current._all_tables
def tables_by_var(var: str): return DataModel._current._tables_by_var[var]
def trees_by_table(table_name: str):                     return DataModel._current._trees_by_table[table_name]
def join_clause_by_tab(table_name: str, going_up: bool): return DataModel._current._join_clause_by_tab[(table_name, going_up)]
def node_by_tab_and_tree(tab: str, tree: str):           return DataModel._current._node_by_tab_and_tree[(tab, tree)]
def tables_by_var_and_tree(var: str, tree: str):         return DataModel._current._tables_by_var_and_tree[(var, tree)]
def dialect(): return DataModel._current._dialect


