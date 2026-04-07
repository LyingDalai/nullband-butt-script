## Context

This is a small script to facilitate the process of fetching nullband.org conf and feeding it to butt app.

## Prerequisites

Make sure you've saved your favorite config in butt first (including favorite device, possibly encoding, etc.)

```
Settings > Main > Configuration > Save
```

## Install

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip requests
```

## Launch

```sh
python3 kick_butt.py
```
