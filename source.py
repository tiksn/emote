import os
import pickle

import sources


# import os.path

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
    trash_directory = '.trash'
    os.makedirs(trash_directory, exist_ok=True)
    pickle_path = os.path.join(trash_directory, 'sources.pickle')
    pickle_data = {}

    if os.path.exists(pickle_path):
        with open(pickle_path, 'rb') as f:
            pickle_data = pickle.load(f)

    imported_sources = import_sources()
    source = imported_sources[kind]
    source_data = {
        "id": source.source_id,
        "source_name": source.source_name
    }
    fetch = getattr(source, "fetch_source")
    characters = fetch()
    source_data["characters"] = map(character_to_dict, characters)
    pickle_data[source.source_id] = source_data

    with open(pickle_path, 'wb') as f:
        pickle.dump(pickle_data, f, protocol=pickle.HIGHEST_PROTOCOL)


def character_to_dict(character: Character):
    return {
        'name': character.Name,
        'profile_url': character.Profile,
        'thumbnail_url': character.Thumbnail,
    }
