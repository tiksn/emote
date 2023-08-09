import os
import pickle

from knack.log import get_logger
from sqlalchemy import insert, create_engine, MetaData, Table, select, update

logger = get_logger(__name__)


def update_repository():
    engine = create_engine(
        "mysql+mysqlconnector://root@127.0.0.1:3306/emote"
    )

    trash_directory = '.trash'
    pickle_path = os.path.join(trash_directory, 'sources.pickle')
    with open(pickle_path, 'rb') as f:
        pickle_data = pickle.load(f)

        with engine.connect() as conn:
            metadata_obj = MetaData()

            characters_table = Table("characters", metadata_obj, autoload_with=engine)
            sources_table = Table("sources", metadata_obj, autoload_with=engine)

            for i, (k, v) in enumerate(pickle_data.items()):

                stmt = select(sources_table).filter_by(id=v['id'].bytes)
                results = conn.execute(stmt)

                if results.rowcount == 0:
                    stmt = insert(sources_table).values([
                        {'id': v['id'].bytes, 'name': v['name']}
                    ])
                    conn.execute(stmt)
                else:
                    stmt = update(sources_table).filter_by(id=v['id'].bytes).values(
                        {'name': v['name']}
                    )
                    conn.execute(stmt)

            for c in v['characters']:

                stmt = select(characters_table).filter_by(id=c['id'].bytes)
                results = conn.execute(stmt)

                if results.rowcount == 0:
                    stmt = insert(characters_table).values([
                        {
                            'id': c['id'].bytes,
                            'source_id': v['id'].bytes,
                            'first_name': c['first_name'],
                            'last_name': c['last_name'],
                            'full_name': c['full_name'],
                            'profile_url': c['profile_url'],
                            'profile_picture_url': c['profile_picture_url'],
                        }
                    ])
                    conn.execute(stmt)
                else:
                    stmt = update(characters_table).filter_by(id=c['id'].bytes).values(
                        {
                            'source_id': v['id'].bytes,
                            'first_name': c['first_name'],
                            'last_name': c['last_name'],
                            'full_name': c['full_name'],
                            'profile_url': c['profile_url'],
                            'profile_picture_url': c['profile_picture_url'],
                        }
                    )
                    conn.execute(stmt)

            conn.commit()
