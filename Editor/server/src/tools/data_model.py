from .settings import Settings
from sapi import setup_sapi, DataModel
from .error import is_err

# you should probably cache this
def make_datamodel(database_name: str = None) -> DataModel | Exception:
    fal_database = Settings.try_load_database(database_name)
    if is_err(fal_database): return fal_database

    setup_sapi(fal_database.dialect, **fal_database.connection_info)
    dataModel = DataModel.from_database(fal_database.dialect, **fal_database.connection_info)
    return dataModel

