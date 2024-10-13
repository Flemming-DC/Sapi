import yaml
import json
from pathlib import Path
from pydantic import BaseModel
from .error import fallible, is_err
from sapi import dialect

_primitive = None | bool | int | float | str
# _JsonishValue =      _primitive | list[_primitive] | list['_Jsonish'] | dict[str, '_JsonishValue']
# _Jsonish = dict[str, _primitive | list[_primitive] | list['_Jsonish'] | dict[str, '_JsonishValue']]

class Database(BaseModel):
    connection_info: dict[str, _primitive]
    dialect: str|dialect.Dialect # starts out as a str, then it gets processed into a Dialect

class Settings(BaseModel):
    databases: dict[str, Database]
    current_database: str

    @staticmethod
    def try_load(): return _try_load()
        

    @staticmethod
    def try_load_database(database_name: str = None) -> Database | Exception:
        fal_settings = _try_load()
        if is_err(fal_settings): return fal_settings
        # if isinstance(fal_settings, Exception): return fal_settings

        if database_name is None:
            database_name = fal_settings.current_database
        return fal_settings.databases[database_name]



@fallible
def _try_load() -> Settings:
    setting_files = [
        '.vscode/sapi_settings.yml',  'sapi_settings.yml',
        '.vscode/sapi_settings.yaml', 'sapi_settings.yaml',
        '.vscode/sapi_settings.json', 'sapi_settings.json',
        ]
    setting_files = [f for f in setting_files if Path(f).exists()]
    
    if len(setting_files) > 1:
        raise Exception(f"Expected exactly one sapi_settings file, found multiple: {setting_files}")
    if len(setting_files) == 0:
        raise Exception("Expected a sapi_settings.yml, sapi_settings.yaml or sapi_settings.json file at "
                        "the project root directory or in a .vscode folder.\n"
                        "Found no such file.")

    setting_file = setting_files[0]
    with open(setting_file) as f: # can raise
        setting_data: dict = json.load(f) if setting_file.endswith('json') else yaml.safe_load(f) # can raise
    
    settings = Settings(**setting_data) # can raise
    _resolve_file_reference_and_dialect(settings) # can raise
    return settings



def _resolve_file_reference_and_dialect(settings: Settings):
    for name, db in settings.databases.items():
        password = _read_password_from_file(db.connection_info) # can raise
        settings.databases[name].connection_info['password'] = password
        settings.databases[name].connection_info.pop('password_file', None) # the seconds argument, prevents a raise

        dialect_str = settings.databases[name].dialect
        settings.databases[name].dialect = dialect.get_or_raise(dialect_str) # can raise


def _read_password_from_file(connection_info: dict[str, _primitive]):
    "read from password file with lots of errorhandling."

    con_keys = list(connection_info.keys())
    if 'password' in con_keys and 'password_file' in con_keys:
        raise Exception("The connection_info for the databases in sapi_settings may either contain "
                        "a key 'password' or a key 'password_file', (which points to a file containing "
                        "the password) or neither, but not both.")
    if 'password_file' not in con_keys:
        return None
    password_file: str = connection_info['password_file']
    if not password_file.endswith('.txt'):
        raise Exception(f"password_file should be a txt file. Found {password_file}.")
    with open(password_file, 'r') as f:
        password = f.readline() # get password
        incorrect_extra_line = f.readline()
        if incorrect_extra_line or not password: # check that this behaves right
            raise Exception(f"password_file should contain exactly one line (with the password). No more and no less.")
        if password.strip(' \t') != password:
            raise Exception(F"Password should not have leading or trailing whitespace (i.e.).")
        password = password.strip('\r') # fck carriage return. We won't hold the user responsible for that windows BS.
    return password






