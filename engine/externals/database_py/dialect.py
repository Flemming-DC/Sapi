import psycopg
import oracledb # probably shouldn't force import of oracledb. Maybe not even psycopg.
from engine.token_tree import TokenType
from . import pep249_database_api_spec_v2

dialect_str = "postgres"


# currently only postgres and oracle are supported
blank_from_clause: dict[str, list[tuple[TokenType, str]]] = {
    'postgres': [],
    'oracle': [
        (TokenType.FROM, 'FROM'),
        (TokenType.VAR, 'dual'),
        ],
}

# currently only postgres is supported
columns_query: dict[str, str] = {
    'postgres': """
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
} 

# currently only postgres is supported
foreign_keys_query: dict[str, str] = {
    'postgres': """
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
} 


_connect: dict[str, pep249_database_api_spec_v2.Connect] = {
    'postgres': psycopg.Connection.connect,
    'oracle': oracledb.connect
}

def connect(*args, **kwargs): 
    return _connect[dialect_str](*args, **kwargs)
