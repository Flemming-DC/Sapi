import traceback
from tools.log import log
from tools.server import server
from tools import event
# from lsprotocol import types as t


# @server.feature(t.TEXT_DOCUMENT_COMPLETION)
# def com(params: t.CompletionParams) -> list[t.CompletionItem] | t.CompletionList | None: 
#     item1 = t.CompletionItem(label='lip')
#     item2 = t.CompletionItem(label='lap')
#     return t.CompletionList(is_incomplete=False, items=[item1, item2])


def main():
    try:
        # features are initialized on import
        from features import executor, hinting
        # from features.highlighter import highlighter
        server.start_io()
        event.on_server_start.occur()
    except Exception as e:
        log(traceback.format_exc())
        raise e


if __name__ == "__main__":
    main()



