import os
import json
import click
import pandas as pd
from tqdm import tqdm
import geopandas as gpd
from ..utils import create_engine, wkb_to_lonlat
from sqlalchemy import text, inspect


@click.command(name='leaderboard')
@click.option('--name')
def export_leaderboard(name=None):
    """Export user actions for an action page organized as a leaderboard."""
    engine = create_engine()

    schema = 'readonly_schema_ourtime'

    insp = inspect(engine)

    sql = text(f"""
      SELECT
        ua.created_at,
        NULLIF(
          TRIM(CONCAT_WS(' ', u.first_name, u.last_name)),
          ''
        ) AS referrer_name,
        u.email AS referrer_email
      FROM {schema}.user_actions ua
      JOIN {schema}.action_pages ap
        ON ap.id = ua.action_page_id
      LEFT JOIN {schema}.users u
        ON u.id = ua.referred_by_user_id
      WHERE ap.name = :name
    """)

    with engine.connect() as conn:
        rows = conn.execute(
            sql,
            {'name': name},
        ).fetchall()

    df = pd.DataFrame(rows, columns=['created_at', 'referrer_name', 'referrer_email'])

    df_counts = (
        df.groupby('referrer_name')['created_at']
        .count()
        .sort_index()
        .sort_values(ascending=False, kind='mergesort')
        .rename('count')
    )

    total = len(df)
    unknown = total - df_counts.sum()

    df_counts = pd.concat([df_counts, pd.Series({'Unknown': unknown, 'Total': total})])

    records = df_counts.to_dict()

    s = json.dumps(records, ensure_ascii=False)

    print(s)
