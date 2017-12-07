import sys


def roadblock(message: str):
    assert isinstance(message, str)
    message += "\nType \'YES\' to confirm: "
    try:
        if input(message) == 'YES':
            return
        else:
            raise KeyboardInterrupt
    except KeyboardInterrupt:
        print('Aborting...')
        sys.exit(2)
