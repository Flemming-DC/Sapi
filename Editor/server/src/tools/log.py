from typing import Any

_max_size = 1000 # const
_has_logged = False
_size = 0

def log(msg: Any):
    """
    Append to log, but clear content from previous run of the program.
    Eliminate this from release.
    """
    global _has_logged, _size
    with open('log.txt', 'r') as f:
        if len(f.read()) > _max_size:
            _has_logged = True
            return
    # if _size > _max_size:
    #     return
    with open('log.txt', 'a' if _has_logged else 'w') as f:
        msg = str(msg) + '\n'
        f.write(msg)
        
        _has_logged = True
        # _size += len(msg)
        # if _size > _max_size:
        #     f.write('...')

