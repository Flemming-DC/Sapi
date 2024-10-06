from typing import Any

_max_size = 1000 # const
_has_logged = False

def log(msg: Any):
    """
    Append to log, but clear content from previous run of the program.
    Eliminate this from release.
    """
    global _has_logged
    if _has_logged:
        with open('log.txt', 'r') as f:
            size = f.read()
            if len(size) > _max_size and size.endswith('...'):
                return
            elif len(size) > _max_size:
                msg = '...'

    with open('log.txt', 'a' if _has_logged else 'w') as f:
        msg = str(msg) + '\n'
        f.write(msg)
        
        _has_logged = True
        # _size += len(msg)
        # if _size > _max_size:
        #     f.write('...')

