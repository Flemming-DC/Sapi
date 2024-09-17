import psycopg
from pathlib import Path
from engine.externals.database_py.forest import Forest
from engine.externals.database_py import dialect
from engine.externals.database_py import deployment

def setup_db_and_make_forest():
    with open('../sapi_secret/pg_password.txt') as f:
        password = f.read()
    connection_info = {'host': 'localhost', 'port': 5432, 'dbname': 'postgres', 'user': 'postgres', 'password': password}

    # these three calls must happen in this order
    deployment.setup(dialect.postgres(), **connection_info)
    setup_test_datamodel(**connection_info)
    return Forest.from_database(dialect.postgres(), **connection_info)


def setup_test_datamodel(**connection_info):
    con = psycopg.Connection.connect(**connection_info)
    cur = con.cursor()
    cur.execute("set search_path to sapi_sys")
    deploy_scripts = sorted([str(f) for f in Path('./test/demo_database').iterdir() if f.name.endswith('.sql')])
    for sql_script in deploy_scripts:
        with open(sql_script) as f:
            cur.execute(f.read())
    con.commit()
    con.close()
