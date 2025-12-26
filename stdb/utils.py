import os
import warnings
import pandas as pd
from shapely import wkb
import sqlalchemy as sql


def create_engine():
    warnings.filterwarnings(
        'ignore',
        category=sql.exc.SAWarning,
        message=r"Did not recognize type 'public\.geography' of column 'lonlat'",
    )

    user = os.environ.get('ST_USER')
    password = os.environ.get('ST_PASSWORD')
    host = os.environ.get('ST_HOST')
    db = os.environ.get('ST_DB')
    ca = os.environ.get('ST_CA')
    engine = sql.create_engine(
        f'postgresql+psycopg://{user}:{password}@{host}:5432/{db}',
        connect_args={
            'sslmode': 'verify-ca',
            'sslrootcert': ca,
        },
    )
    return engine


def wkb_to_lonlat(hex_wkb):
    if hex_wkb is None:
        return None, None
    geom = wkb.loads(bytes.fromhex(hex_wkb))
    lon, lat = geom.x, geom.y
    return lon, lat


def create_logger(prefix):
    def logger(string):
        print(prefix + ' ' + string)

    return logger
