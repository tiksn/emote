import os
from uuid import UUID

from knack.log import get_logger
from sqlalchemy import create_engine, MetaData, Table, select

logger = get_logger(__name__)


class Persona:
    def __init__(self, _id, first_name, last_name, full_name, profile_picture_url):
        self.ID = _id
        self.FirstName = first_name
        self.LastName = last_name
        self.FullName = full_name
        self.ProfilePictureUrl = profile_picture_url


class Origin:
    def __init__(self, _id, _name):
        self.ID = _id
        self.Name = _name


def module_names():
    folder = os.path.join(os.path.split(__file__)[0], 'targets')
    for name in os.listdir(folder):
        if name.endswith(".py") and not name.startswith("__"):
            yield name[:-3]


def import_targets():
    names = list(module_names())
    m = __import__('targets', globals(), locals(), names, 0)
    return dict((name, getattr(m, name)) for name in names)


def populate_target(kind: str, api_key: str):
    imported_targets = import_targets()
    target = imported_targets[kind]
    populate = getattr(target, "populate_target")

    engine = create_engine(
        "mysql+mysqlconnector://root@127.0.0.1:3306/emote"
    )

    with engine.connect() as conn:
        metadata_obj = MetaData()

        characters_table = Table("characters", metadata_obj, autoload_with=engine)
        sources_table = Table("sources", metadata_obj, autoload_with=engine)

        stmt = select(sources_table)
        source_results = conn.execute(stmt)

        origins = []
        personas = dict()

        for source_id, source_name in source_results:
            origin_id = UUID(bytes=bytes(source_id))
            origin_name = source_name

            origin = Origin(origin_id, origin_name)
            origins.append(origin)
            personas[origin_id] = []

        stmt = select(characters_table)
        character_results = conn.execute(stmt)

        for character_id, source_id, character_first_name, character_last_name, character_full_name, character_profile_url, character_profile_picture_url in character_results:
            character_id = UUID(bytes=bytes(character_id))
            origin_id = UUID(bytes=bytes(source_id))

            persona = Persona(character_id, character_first_name, character_last_name, character_full_name,
                              character_profile_picture_url)
            personas[origin_id].append(persona)

        populate(api_key, origins, personas)
