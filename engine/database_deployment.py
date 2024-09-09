import os
# import pathlib
from pathlib import Path
from psycopg import Connection
from psycopg.rows import dict_row # this only allows access by name, not index :(


sql_folder = Path('./engine/database')
sql_scripts = sorted([str(f) for f in sql_folder.iterdir() if f.name.endswith('.sql')])


def setup():
    sql_folder = './engine/database'
    sql_scripts: list[str] = os.listdir(sql_folder) # get files and sub-directories
    sql_scripts = [f for f in sql_scripts if f.endswith('.sql')] # or perhaps f.endswith('.sapi')
    sql_scripts.sort()

    deployment_queries: list[str] = []
    for sql_script in sql_scripts:
        with open(sql_script) as f:
            deployment_queries += f.read()

    with open('../sapi_secret/pg_password.txt') as f:
        password = f.read()
    with Connection.connect(host='localhost', port = 5432, dbname = 'postgres', user = 'postgres', password=password) as con:
        with con.cursor(row_factory=dict_row) as cur:
            cur.execute("set search_path to sapi_sys")
            for query in deployment_queries:
                cur.execute(query)




