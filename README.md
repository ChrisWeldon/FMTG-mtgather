---
title: mtgather
created: '2020-11-11T21:59:06.226Z'
modified: '2020-11-11T22:10:32.575Z'
---

# mtgather

A library containing modules used to interact with a database and webpages holding Magic: the Gathering card occurance information and pricing history.

To install:
```
pip install git+https://github.com/ChrisWeldon/FMTG-mtgather.git
```

API reference can be found here at http://www.chriswevans.com/FMTG/mtgather

## Usage
To connect library to mysql Database:
Setup environment variable ```GATHERCONFIG = 'path/to/config.json'```

The configuration file:
```
{
  "database": {
      "database_name": <name-of-database>,
      "dev_database_name" : <name-of-dev-database>,
      "user":<login-user>,
      "password":<login-password>,
      "host":<host-ip-or-domain>,
      "use_pure": <use-pure-acces> // FALSE suggested
    },
  "path": <path to log files>, // Deprecated, replaced soon
  "dev": <boolean-in-dev-mode>, // Deprecated, replaced soon
}

```
