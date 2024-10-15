import traceback
from tools.log import log
from tools.server import server
from tools import event

def main():
    try:
        # features are initialized on import
        from features import executor, highlighter, hinting
        server.start_io()
        event.on_server_start.occur()
    except Exception as e:
        log(traceback.format_exc())
        raise e


if __name__ == "__main__":
    main()



