from pathlib import Path
from .pep249_database_api_spec_v2 import Connection, Cursor
from .dialect import Dialect


def setup_sapi(dialect: Dialect, cur: Cursor, sapi_sys_schema: str):
    if is_deployed(cur, dialect, sapi_sys_schema):
        return
    
    print("setting up sapi system tables")
    builtin_deploy_scripts = sorted([str(f) for f in Path(dialect.sapi_deploy_folder).iterdir() if f.name.endswith('.sql')])
    for sql_script in builtin_deploy_scripts:
        with open(sql_script) as f:
            cur.execute(f.read().replace('sapi_sys', sapi_sys_schema))


def is_deployed(cur: Cursor, dialect: Dialect, sapi_sys_schema: str) -> bool:
    cur.execute("savepoint deployment_is_deployed")
    cur.execute(f"with columns as ({dialect.columns_query})"
        + f"select distinct table_name from columns where schema_name = '{sapi_sys_schema}'")
    actual_sapi_sys_tables = {row[0] for row in cur.fetchall()}
    cur.execute("rollback to savepoint deployment_is_deployed")
    expected_sapi_sys_tables = {'sapi_trees', 'sapi_tables'}

    if actual_sapi_sys_tables == expected_sapi_sys_tables:
        return True
    if not actual_sapi_sys_tables:
        return False
    
    msg = f"""
        Some but not all of the sapi system tables exist. This seems to be an error.
        Expected: {list(expected_sapi_sys_tables)}
        Found: {list(actual_sapi_sys_tables)}
        Missing: {[t for t in expected_sapi_sys_tables if t not in actual_sapi_sys_tables]}
        
        Hint: Consider making a backup of the data in the sapi system tables and recreating them 
        by calling this function again. Next copy the data back into the sapi system tables.
        """
    raise Exception(msg)

