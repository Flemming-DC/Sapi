from .token_tree import TokenType


dialect_str = "postgres"


blank_from_clause: dict[str, list[tuple[TokenType, str]]] = {
    'postgres': [],
    'oracle': [
        (TokenType.FROM, 'FROM'),
        (TokenType.VAR, 'dual'),
        ],
}

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

