import click
from . import (
    inspect_table,
)


@click.group()
def inspect():
    """Inspect Soldarity Tech db."""
    pass


inspect.add_command(inspect_table.inspect_table)
