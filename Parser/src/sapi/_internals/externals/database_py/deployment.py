from pathlib import Path
from .pep249_database_api_spec_v2 import Cursor
from .dialect import Dialect


def setup_sapi(dialect: Dialect, **connection_info):
    con = dialect.connect(**connection_info)
    cur = con.cursor()
    if is_deployed(cur, dialect):
        return
    
    print("setting up sapi system tables")
    builtin_deploy_scripts = sorted([str(f) for f in Path(dialect.sapi_deploy_folder).iterdir() if f.name.endswith('.sql')])
    for sql_script in builtin_deploy_scripts:
        with open(sql_script) as f:
            cur.execute(f.read())
    con.commit()
    con.close()


def is_deployed(cur: Cursor, dialect: Dialect) -> bool:
    cur.execute(f"with columns as ({dialect.columns_query})"
        + "select distinct table_name from columns where schema_name = 'sapi_sys'")
    actual_sapi_sys_tables = {row[0] for row in cur.fetchall()}
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

