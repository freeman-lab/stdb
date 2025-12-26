import os
import json
import click
import pandas as pd
from tqdm import tqdm
import geopandas as gpd
from ..utils import create_engine, wkb_to_lonlat
from sqlalchemy import text, inspect


@click.command(name='table')
@click.argument('name')
def inspect_table(name):
    """Export current events to a file."""
    engine = create_engine()

    schema = 'readonly_schema_ourtime'

    insp = inspect(engine)

    cols = insp.get_columns(name, schema='readonly_schema_ourtime')

    for col in cols:
        print(col)
