# XDCC series autodownloader

This software downloads new episode from the series described in the configuration file.

# Execution

`xdcc-series-autodl [configuration file]`

If the software is run without parameters it will process the `series.yaml` file present
in the same folder as the application.

# Configuration file format

The configuration file is in YAML format and can be edited with any text editor.

Each series must contain a four (or five) lines entry in the configuration file with the following format:

```
name of the series:
  download folder: c:/path/to/your/folder
  last episode downloaded: 0
  search engine: engine of choice
  search string: 'search string here'
```

An example functional file would be:
```
magi:
  download folder: d:/Downloads
  last episode downloaded: 0
  search engine: horriblesubs
  search string: '[HorribleSubs] Magi - {:02} [1080p]'
```

The `last episode downloaded` field will be updated automatically each time
the application is run.

The `search engine` field should contain one of the following options:
- horriblesubs
- ixirc
- nibl

The search string should be as precise as possible, and it should be built
using Python formatting syntax for insertion of the episode number.

E.g. the string 'Magi - {}' will search for:
`Magi - 1, Magi - 2, ... Magi - 3`

And the string 'Magi - {:02}' will search for:
`Magi - 01, Magi - 02, ... Magi - 03.`

There is an additional optional configuration line for each series:
`preferred bot: bot of choice`

If preferred bot is not set, the first bot in the search result will be used.
