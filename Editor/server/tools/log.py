from typing import Any

_max_size = 100000 # const
_has_logged = False

def log(*msg: Any):
    """
    Append to log, but clear content from previous run of the program.
    Eliminate this from release.
    We do not mark it as fallible, it doesnt go in release, and tracebacks are nice in development.
    """
    global _has_logged
    if isinstance(msg, (tuple, list)):
        msg = ' '.join(str(m) for m in msg)
    if _has_logged:
        with open('log.txt', 'r') as f:
            text = f.read()
            if len(text) > _max_size and text.rstrip().endswith('...'):
                return
            elif len(text) > _max_size:
                msg = '...'

    mode = 'a' if _has_logged else 'w'
    with open('log.txt', mode) as f:
        msg = str(msg) + '\n'
        f.write(msg)
        
        _has_logged = True
        # _size += len(msg)
        # if _size > _max_size:
        #     f.write('...')

