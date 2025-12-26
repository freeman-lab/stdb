import os
import json
import click
import pandas as pd
from tqdm import tqdm
import geopandas as gpd
from ..utils import create_engine, wkb_to_lonlat
from sqlalchemy import text, inspect


@click.command(name='events')
@click.option('--name')
def export_events(name=None):
    """Export data about current events."""
    engine = create_engine()

    schema = 'readonly_schema_ourtime'

    insp = inspect(engine)

    sql = text(f"""
        SELECT
            meci.id,
            ap.name,
            meci.start_time,
            meci.end_time,
            meci.location_name,
            meci.location_address,
            meci.lonlat,
            ap.url_slug,
            COUNT(DISTINCT rsvp.user_id) AS rsvp_count
        FROM {schema}.mobilize_event_calendar_items AS meci
        JOIN {schema}.mobilize_events AS me
          ON me.id = meci.mobilize_event_id
        JOIN {schema}.action_pages AS ap
          ON ap.id = me.action_page_id
        LEFT JOIN {schema}.mobilize_event_rsvps AS rsvp
          ON rsvp.mobilize_event_calendar_item_id = meci.id
        WHERE meci.start_time >= (now() AT TIME ZONE 'America/New_York')::date
          AND (CAST(:name AS text) IS NULL OR ap.name ILIKE CAST(:name AS text) || '%')
        GROUP BY
            meci.id,
            ap.name,
            meci.start_time,
            meci.end_time,
            meci.location_name,
            meci.location_address,
            meci.lonlat,
            ap.url_slug
        ORDER BY meci.start_time ASC
    """)

    with engine.connect() as conn:
        rows = conn.execute(
            sql,
            {'name': name},
        ).fetchall()

    df = pd.DataFrame(
        rows,
        columns=[
            'id',
            'title',
            'start_time',
            'end_time',
            'location_name',
            'location_address',
            'wkb',
            'url_slug',
            'rsvps',
        ],
    )
    lons, lats = zip(*df['wkb'].map(wkb_to_lonlat))
    df['lon'] = lons
    df['lat'] = lats
    df['url'] = df['url_slug'].apply(lambda d: 'https://act.ourtime.nyc/' + d)
    df['start_time'] = (
        df['start_time'].dt.tz_localize('UTC').dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    )
    df['end_time'] = (
        df['end_time'].dt.tz_localize('UTC').dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    )
    df = df.drop(columns=['wkb', 'url_slug'])

    gdf_points = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df['lon'], df['lat']),
        crs='EPSG:4326',
    )

    boroughs = gpd.read_file('data/new-york-city-boroughs.geojson').to_crs('EPSG:4326')

    out = gpd.sjoin(
        gdf_points,
        boroughs[['name', 'geometry']],
        how='left',
        predicate='intersects',
    )

    df['borough'] = out['name'].values

    records = df.to_dict(orient='records')
    s = json.dumps(records, ensure_ascii=False)
    print(s)
