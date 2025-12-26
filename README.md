# stdb

> Solidarity Tech database CLI

# about

This repo contains a CLI tool built in Python for interfacing with Solidarity Tech. It's mainly designed to pull together various access patterns that show up consistently in a campaign, and will be expanded over time.

*Work in progress*

# installation

Packaging is handled by poetry. To install, just use

```
poetry install
```

And then to run commands do

```
poetry run stdb <command> <args>
```

You need to have an `.env` file that specifies several environmental variables:

`ST_HOST` host name for the read-only db mirror
`ST_USER` user name for the read-only db mirror
`ST_PASSWORD` password for the read-only db mirror
`ST_DB` db name for the read-only db mirror
`ST_CA` certificate authorty for the read-only db mirror

# commands

The commands currently available are:

- `stdb export events` - export a table of data about events
- `stdb export leaderboard` - export a leaderboard-style table of user actions
- `stdb inspect table` - inspect the schema of a table