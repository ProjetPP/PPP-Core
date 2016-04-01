"""Store whole answers to a database, for profiling purposes."""

import json

from sqlalchemy import create_engine
from sqlalchemy import Table, Column
from sqlalchemy import Boolean, Float, Integer, String, Text, DateTime
from sqlalchemy import MetaData, ForeignKey

metadata = MetaData()

requests = Table('requests', metadata,
                 Column('request_handling_start_time', Float),
                 Column('request_handling_end_time', Float),
                 Column('request_answers_json', Text),
                )

def get_engine(uri):
    """Asks SQLAlchemy to create an engine to connect to the URI and return it."""
    engine = create_engine(uri)
    metadata.create_all(engine)
    return engine

def log_answers(config, answers, start_time, end_time):
    url = config.verbose_log_url
    if not url:
        return
    conn = get_engine(url).connect()
    answers = json.dumps([x.as_dict() for x in answers])
    ins = requests.insert().values(
            request_handling_start_time=start_time,
            request_handling_end_time=end_time,
            request_answers_json=answers)
    res = conn.execute(ins)
