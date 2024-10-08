from __future__ import annotations
import sqlglot
from typing import Callable
from sapi._internals.token_tree import TokenType
from .pep249_database_api_spec_v2 import Connect, Connection
from dataclasses import dataclass

@dataclass
class Dialect:
    _name: str
    blank_from_clause: str
    columns_query: str
    foreign_keys_query: str
    connect: Connect
    sapi_deploy_folder: str # ehh... ugly
    _set_to_read_only: Callable[[Connection], None] = lambda: None # optional parameter

    def __post_init__(_):
        _._sqlglot_dialect = sqlglot.Dialect.get_or_raise(_._name)
        _._blank_from_clause: list[tuple[TokenType, str]] = [(t.token_type, t.text) 
            for t in _._sqlglot_dialect.tokenize(_.blank_from_clause)]

    def sqlglot_dialect(_): return _._sqlglot_dialect
    def blank_from_clause_tokens(_): return _._blank_from_clause


def get_or_raise(dialect_name: str):
    if dialect_name == 'postgres': return postgres()
    # elif dialect_name == 'oracle': return oracle()
    # ...
    else: raise ValueError(
        "This dialect is not yet implemented in sapi. You must instantiate the dialect class to implement the dialect.")

def postgres():
    import psycopg
    def set_to_read_only(con: psycopg.Connection): con.read_only = True
    return Dialect(
        _name = "postgres",
        blank_from_clause = "",
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
                and tab.relkind = 'r' -- filter out non-table objects in pg_class (e.g. views, sequences etc.)
                and schema.nspname not in ('pg_catalog', 'pg_toast', 'information_schema')
            """,
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
                and col.attnum > 0      -- exclude system columns
                and fcol.attnum > 0     -- exclude system columns
                and tab.relkind = 'r'   -- filter out non-table objects in pg_class (e.g. views, sequences etc.)
                and ftab.relkind = 'r'  -- filter out non-table objects in pg_class (e.g. views, sequences etc.)
                and not col.attisdropped 
                and not fcol.attisdropped 
            """,
        sapi_deploy_folder = "./engine/externals/database_sql",
        connect = psycopg.Connection.connect,
        _set_to_read_only = set_to_read_only,
    )

# def oracle():
#     import oracledb
#     return Dialect(
#         name = "oracle",
#         blank_from_clause = "from dual",
#         columns_query = missing,
#         foreign_keys_query = missing,
#         sapi_deploy_folder = missing,
#         connect = oracledb.connect,
#         _set_to_read_only = missing,
#     )



