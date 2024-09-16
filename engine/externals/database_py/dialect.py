from __future__ import annotations
import sqlglot
from engine.token_tree import TokenType
from . import pep249_database_api_spec_v2
from dataclasses import dataclass

@dataclass
class Dialect:
    name: str
    blank_from_clause: str
    columns_query: str
    foreign_keys_query: str
    connect: pep249_database_api_spec_v2.Connect

    def __post_init__(_):
        _._sqlglot_dialect = sqlglot.Dialect.get_or_raise(_.name)
        _._blank_from_clause: list[tuple[TokenType, str]] = [(t.token_type, t.text) 
            for t in _._sqlglot_dialect.tokenize(_.blank_from_clause)]

    def sqlglot_dialect(_): return _._sqlglot_dialect
    def blank_from_clause_tokens(_): return _._blank_from_clause



def postgres():
    import psycopg
    return Dialect(
        name = "postgres",
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
                and col.attnum > 0 -- exclude system columns
                and fcol.attnum > 0 -- exclude system columns
                and not col.attisdropped 
                and not fcol.attisdropped 
            """,
        connect = psycopg.Connection.connect,
    )

# def oracle():
#     import oracledb
#     return Dialect(
#         name = "oracle",
#         blank_from_clause = "from dual",
#         columns_query = missing,
#         foreign_keys_query = missing,
#         connect = oracledb.connect,
#     )


# current = postgress() # temp
