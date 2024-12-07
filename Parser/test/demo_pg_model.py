import psycopg, getpass
from pathlib import Path
from sapi import setup_sapi, dialect, DataModel, Database

_sys_schema = "sapi_sys"
_demo_schema = "sapi_demo"

def setup_db_and_make_datamodel():
    database = Database(
        sys_schema = sys_schema(),
        dialect = dialect.postgres(),
        startup_script = "",
        connect_kwargs = get_connection_info(),
        )
    
    with psycopg.Connection.connect(**database.connect_kwargs) as con, con.cursor() as cur:
        set_demo_searchpath(cur)
        setup_sapi(dialect.postgres(), cur, database.sys_schema)
        setup_test_datamodel(cur, database.sys_schema)
        datamodel = DataModel.from_database(database.dialect, cur, database.sys_schema)
        con.commit()
    # # these three calls must happen in this order
    # with Transaction(database) as tr:
    #     setup_sapi(dialect.postgres(), tr.cursor(), database.sys_schema)
    #     setup_test_datamodel(tr.cursor(), database.sys_schema)
    #     datamodel = DataModel.from_database(database.dialect, tr.cursor(), database.sys_schema)
    #     tr.connection().commit()
    return datamodel


def setup_test_datamodel(cursor: psycopg.Cursor, sys_schema: str):
    deploy_scripts = sorted([str(f) for f in Path('./test/demo_database').iterdir() if f.name.endswith('.sql')])
    # cursor.execute(f"set search_path to {sys_schema}")
    for sql_script in deploy_scripts:
        with open(sql_script) as f:
            code = f.read()
            cursor.execute(code.replace('sapi_sys', sys_schema))

def set_demo_searchpath(cur: psycopg.Cursor):
    cur.execute(f"set search_path to {demo_schema()}")


def get_connection_info() -> dict[str, str|int]:
    # return {'service': 'udv_d0003', 'user': getpass.getuser().lower() }
    password_path = Path('sapi_secret/pg_password.txt')
    while not password_path.exists():
        password_path = '..' / password_path # go up the file tree until we find password file
    with open(password_path) as f:
        password = f.read()
    connection_info = {'host': 'localhost', 'port': 5432, 'dbname': 'postgres', 'user': 'postgres', 'password': password}
    return connection_info

def demo_schema(): return _demo_schema
def sys_schema(): return _sys_schema

