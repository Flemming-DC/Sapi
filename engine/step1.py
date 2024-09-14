from textwrap import dedent
from psycopg import Connection, Cursor
from psycopg.rows import dict_row, DictRow # this only allows access by name, not index :(
import database_deployment
from dataclasses import dataclass
from typing import Callable
from pprint import pprint

# postgres
columns_query = """
    SELECT 
        schema.nspname as schema_name,
        tab.relname as table_name,
        col.attname as column_name
    FROM pg_namespace  AS schema
    JOIN pg_class      AS tab ON tab.relnamespace = schema.oid
    JOIN pg_attribute  AS col ON col.attrelid = tab.oid    
    WHERE col.attnum > 0 -- exclude system columns
        and not col.attisdropped   
        and schema.nspname not in ('pg_catalog', 'pg_toast', 'information_schema')
    """

# postgres
foreign_keys_query = """
    SELECT
        schema.nspname  as schema,
        fschema.nspname as referenced_schema,
        tab.relname     AS table,
        ftab.relname    AS referenced_table,
        col.attname     AS primary_key_col, -- note that a pk can contain multiple columns
        fcol.attname    AS foreign_key_col -- note that a fk can contain multiple columns
    FROM pg_constraint AS con
    JOIN pg_class      AS tab     ON tab.oid = con.conrelid
    JOIN pg_namespace  AS schema  ON schema.oid = tab.relnamespace
    JOIN pg_attribute  AS col     ON col.attnum = ANY(con.conkey) AND col.attrelid = con.conrelid
    JOIN pg_class      AS ftab    ON ftab.oid = con.confrelid
    JOIN pg_namespace  AS fschema ON fschema.oid = ftab.relnamespace
    JOIN pg_attribute  AS fcol    ON fcol.attnum = ANY(con.confkey) AND fcol.attrelid = con.confrelid
    WHERE con.contype = 'f'
        and col.attnum > 0 -- exclude system columns
        and fcol.attnum > 0 -- exclude system columns
        and not col.attisdropped 
        and not fcol.attisdropped 
    """

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

def with_cursor(func: Callable):
    database_deployment.setup()
    with open('../sapi_secret/pg_password.txt') as f:
        password = f.read()
    with Connection.connect(host='localhost', port = 5432, dbname = 'postgres', user = 'postgres', password=password) as con:
        with con.cursor(row_factory=dict_row) as cur:
            cur.execute("set search_path to sapi_sys")
            func(cur)


def make_trees(cur: Cursor[DictRow]):
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

# pprint([(t.name, t.parent) for t in trees[0].tables])
# pprint([(t.name, t.parent) for t in trees[1].tables])


if __name__ == '__main__':
    with_cursor(make_trees)

