import platform


def get_slash():
    system = platform.system()
    if system == 'Darwin' or system == 'Linux':
        return '/'
    else:
        return '\\'
