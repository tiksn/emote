import os
import sources


class Character:
    def __init__(self, name, profile, thumbnail):
        self.Name = name
        self.Profile = profile
        self.Thumbnail = thumbnail


def module_names():
    folder = os.path.split(sources.__file__)[0]
    for name in os.listdir(folder):
        if name.endswith(".py") and not name.startswith("__"):
            yield name[:-3]


def import_sources():
    names = list(module_names())
    m = __import__(sources.__name__, globals(), locals(), names, 0)
    return dict((name, getattr(m, name)) for name in names)


def fetch_source(kind: str):
    sources = import_sources()
    source = sources[kind]
    fetch = getattr(source, "fetch_source")
    return fetch()
