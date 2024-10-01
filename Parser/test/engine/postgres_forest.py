import psycopg
from pathlib import Path
from sapi.externals.database_py.forest import Forest
from sapi.externals.database_py import dialect
from sapi.externals.database_py import deployment


def setup_db_and_make_forest():
    connection_info = get_connection_info()
    # these three calls must happen in this order
    deployment.setup(dialect.postgres(), **connection_info)
    setup_test_datamodel(**connection_info)
    return Forest.from_database(dialect.postgres(), **connection_info)


def setup_test_datamodel(**connection_info):
    deploy_scripts = sorted([str(f) for f in Path('./test/demo_database').iterdir() if f.name.endswith('.sql')])
    with psycopg.Connection.connect(**connection_info) as con:
        with con.cursor() as cur:
            cur.execute("set search_path to sapi_sys")
            for sql_script in deploy_scripts:
                with open(sql_script) as f:
                    cur.execute(f.read())
    


def get_connection_info() -> dict[str, str|int]:
    password_path = Path('sapi_secret/pg_password.txt')
    while not password_path.exists():
        password_path = '..' / password_path # go up the file tree until we find password file
    with open(password_path) as f:
        password = f.read()
    connection_info = {'host': 'localhost', 'port': 5432, 'dbname': 'postgres', 'user': 'postgres', 'password': password}
    return connection_info
