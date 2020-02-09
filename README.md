# XDCC series autodownloader

This software downloads new episode from the series described in the configuration file.

# Execution

```
usage: xdcc-series-autodl.py [-h] [-v] [-s SERIES]

XDCC Series Autodownloader

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Output additional process details
  -s SERIES, --series SERIES
                        YAML file with series configuration
```

If the software is run without parameters it will process the `series.yaml` file present
in the same folder as the application.

# Configuration file format

The configuration file is in YAML format and can be edited with any text editor.
The configuration file is composed by two sections: defaults, and series.

## Defaults section

The default sections contain configuration for some parameters that are applied to the series to download
in case these parameters are not overriden for the specific series:

The following parametrers can be configured in the defaults section:

```
defaults:
  download folder: d:/Downloads
  episode download limit per execution: 1
  preferred bot: Ginpachi-Sensei
  search engine: horriblesubs
```

- The `download folder` parameter configures the default download location for episodes.
- The `episode download limit per execution` parameter configures how many episodes per series can be downloaded on each program execution.
- The `preferred bot` parameter configures which is the preferred bot to download from.
- The `search engine` parameter configures what is the default search engine to use for searching episodes. The following search engines are supported:
  `horriblesubs`, `ixirc`, and `nibl`.

Any of this parameters can be overriden in the specific series section.

## Series section

The series section should contain the configuration for each series to be downloaded.

Each series must contain at least one configuration entry: `search string`.
Additionally a series configuration entry might override any of the parameters from the `defaults` section.

The search string should be as precise as possible, and it should be built
using Python formatting syntax for insertion of the episode number.

E.g. the string 'Magi - {}' will search for:
`Magi - 1, Magi - 2, ... Magi - 3`

And the string 'Magi - {:02}' will search for:
`Magi - 01, Magi - 02, ... Magi - 03.`

The following example presents a series section containing one serie:
```
series:
  magi:
    download folder: d:/Downloads
    last episode downloaded: 0
    search engine: horriblesubs
    search string: '[HorribleSubs] Magi - {:02} [1080p]'
```

The `last episode downloaded` field will be updated automatically each time
the application is run. If this field does not exist, it will be created
automatically by the program, starting at 0.


### Skipping (download pause) series

If the name of the series starts with "skip-" it will be skipped during the download process.
This feature can be used to pause downloading of a series without removing it from the YAML file.

E.g.:
```
skip-magi:
  download folder: d:/Downloads
  last episode downloaded: 0
  search engine: horriblesubs
  search string: '[HorribleSubs] Magi - {:02} [1080p]'
```

## Full configuration file example

The example below presents a fully functional configuration file:

```
defaults:
  download folder: d:/Downloads
  episode download limit per execution: 3
  preferred bot: Ginpachi-Sensei
  search engine: horriblesubs
series:
  magi:
    download folder: d:/Downloads
    last episode downloaded: 0
    search engine: horriblesubs
    search string: '[HorribleSubs] Magi - {:02} [1080p]'
```