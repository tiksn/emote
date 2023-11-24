import logging
import os
import pickle
from enum import Enum

from knack.log import get_logger

import sources

logger = get_logger(__name__)


class CharacterType(Enum):
    ANTAGONIST = -1
    UNKNOWN = 0
    PROTAGONIST = 1
    DEUTERAGONIST = 2
    TRITAGONIST = 3


class CharacterSource:
    def __init__(self, _id, short_name, long_name):
        self.ID = _id
        self.ShortName = short_name
        self.LongName = long_name
        self.Characters = []


class Character:
    def __init__(self, _id, first_name, last_name, full_name, _type, profile_url, profile_picture_url):
        self.ID = _id
        self.FirstName = first_name
        self.LastName = last_name
        self.FullName = full_name
        self.Type = _type
        self.ProfileUrl = profile_url
        self.ProfilePictureUrl = profile_picture_url


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

    fetch = getattr(source, "fetch_source")
    characters_sources = fetch()

    for character_source in characters_sources:
        source_data = {
            "id": character_source.ID,
            "name": character_source.LongName,
            "characters": list(map(character_to_dict, character_source.Characters)),
        }
        pickle_data[character_source.ID] = source_data

    with open(pickle_path, 'wb') as f:
        pickle.dump(pickle_data, f, protocol=pickle.HIGHEST_PROTOCOL)

    for key, value in pickle_data.items():
        logging.info(f"Extracted {len(value['characters'])} characters from '{value['name']}' ({value['id']})")
        for character in value['characters']:
            logging.info(f"'{character['first_name']}' '{character['last_name']}' - '{character['full_name']}'")


def character_to_dict(character: Character):
    return {
        'id': character.ID,
        'first_name': character.FirstName,
        'last_name': character.LastName,
        'full_name': character.FullName,
        'type': character.Type.value,
        'profile_url': character.ProfileUrl,
        'profile_picture_url': character.ProfilePictureUrl,
    }
