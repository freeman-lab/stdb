import click
from . import export_events, export_leaderboard


@click.group()
def export():
    """Export data from Soldarity Tech."""
    pass


export.add_command(export_events.export_events)
export.add_command(export_leaderboard.export_leaderboard)
