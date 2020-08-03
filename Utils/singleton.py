singleton_dict = {}


def set_attr(name: str, content):
    singleton_dict[name] = content


def get_attr(name: str):
    if not key_in_singleton(name):
        return None
    return singleton_dict[name]


def key_in_singleton(name: str):
    return name in singleton_dict.keys()


def set_access_log(access_log: str):
    set_attr('access_log', access_log)


def get_access_log():
    return get_attr('access_log')
