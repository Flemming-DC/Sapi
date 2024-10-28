import psycopg
from pathlib import Path
from sapi import setup_sapi, dialect, DataModel, Transaction, Database


def setup_db_and_make_datamodel():
    database = Database(
        dialect = dialect.postgres(),
        startup_script = "",
        connect_kwargs = get_connection_info(),
        )
    sapi_sys_schema = 'sapi_sys'
    # these three calls must happen in this order
    with Transaction(database) as tr:
        setup_sapi(dialect.postgres(), tr.cursor(), sapi_sys_schema)
        setup_test_datamodel(tr.cursor(), sapi_sys_schema)
        datamodel = DataModel.from_database(database.dialect, tr.cursor(), sapi_sys_schema)
        tr.connection().commit()
    return datamodel


def setup_test_datamodel(cursor: psycopg.Cursor, sapi_sys_schema: str):
    deploy_scripts = sorted([str(f) for f in Path('./test/demo_database').iterdir() if f.name.endswith('.sql')])
    # cursor.execute("set search_path to sapi_sys")
    for sql_script in deploy_scripts:
        with open(sql_script) as f:
            cursor.execute(f.read().replace('sapi_sys', sapi_sys_schema))
    

def get_connection_info() -> dict[str, str|int]:
    password_path = Path('sapi_secret/pg_password.txt')
    while not password_path.exists():
        password_path = '..' / password_path # go up the file tree until we find password file
    with open(password_path) as f:
        password = f.read()
    connection_info = {'host': 'localhost', 'port': 5432, 'dbname': 'postgres', 'user': 'postgres', 'password': password}
    return connection_info
