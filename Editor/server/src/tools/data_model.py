from .settings import Settings
from sapi import setup_sapi, DataModel
# from tools.server import server
from .fallible import Fallible, ok, err

# you should probably cache this
def make_datamodel(database_name: str) -> Fallible[DataModel]:
    fal_settings = Settings.try_load()
    if not fal_settings: 
        return err("Failed to load datamodel, due to error in settings file:\n" + str(fal_settings.err))

    # server.send_notification("hi. server is here")
    # server.show_message(sapi_demo.get_sql())

    database = fal_settings.ok.databases[database_name]
    setup_sapi(database.dialect, **database.connection_info)
    dataModel = DataModel.from_database(database.dialect, **database.connection_info)
    return ok(dataModel)

