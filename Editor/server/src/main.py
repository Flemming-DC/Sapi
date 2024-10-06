import traceback
from tools.log import log
from tools.server import server

def main():
    try:
        # features are initialized on import
        from features import demo_features, executor, document
        server.start_io()
    except Exception as e:
        log(traceback.format_exc())
        raise e


if __name__ == "__main__":
    main()



