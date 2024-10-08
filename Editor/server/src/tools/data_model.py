from .settings import Settings
from sapi import setup_sapi, DataModel
# from tools.server import server
from .fallible import Fallible, ok, err

# you should probably cache this
def make_datamodel(database_name: str = None) -> Fallible[DataModel]:
    fal_settings = Settings.try_load()
    if not fal_settings: 
        return err("Failed to load datamodel, due to error in settings file:\n" + str(fal_settings.err))

    if database_name is None:
        database_name = fal_settings.ok.current_database
    database = fal_settings.ok.databases[database_name]
    setup_sapi(database.dialect, **database.connection_info)
    dataModel = DataModel.from_database(database.dialect, **database.connection_info)
    return ok(dataModel)

