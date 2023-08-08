import os
import pickle

from knack.log import get_logger
from sqlalchemy import insert, create_engine, text, MetaData, Table

logger = get_logger(__name__)


def update_repository():
    engine = create_engine(
        "mysql+mysqlconnector://root@127.0.0.1:3306/emote"
    )
    with engine.connect() as conn:
        metadata_obj = MetaData()

        characters_table = Table("characters", metadata_obj, autoload_with=engine)
        sources_table = Table("sources", metadata_obj, autoload_with=engine)

        trash_directory = '.trash'
        pickle_path = os.path.join(trash_directory, 'sources.pickle')
        with open(pickle_path, 'rb') as f:
            pickle_data = pickle.load(f)
            for i, (k, v) in enumerate(pickle_data.items()):
                stmt = insert(sources_table).values([
                    {'id': v['id'].bytes, 'name': v['name']}
                ])
                conn.execute(stmt)
                conn.commit()
