from .settings import Settings
from sapi import setup_sapi, DataModel

# you should probably cache this
def make_datamodel(database_name: str = None) -> DataModel:
    fal_database = Settings.load_database(database_name)
    setup_sapi(fal_database.dialect, **fal_database.connection_info)
    dataModel = DataModel.from_database(fal_database.dialect, **fal_database.connection_info)
    return dataModel

