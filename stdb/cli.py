import click
from dotenv import load_dotenv
from stdb.commands import export, inspect

load_dotenv()


@click.group()
def cli():
    """Command line interface for Solidarity Tech."""
    pass


cli.add_command(export.export)
cli.add_command(inspect.inspect)
