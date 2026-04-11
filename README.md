## Context

This is a small script to facilitate the process of fetching nullband.org conf and feeding it to butt app.

## Prerequisites

Make sure you've saved your favorite config in butt first (including favorite device, possibly encoding, etc.)

```
Settings > Main > Configuration > Save
```

## Install

```sh
MY_BUTT="~/my_butt/" # or whatever folder you want to install this to
cd "$MY_BUTT"
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip requests
```

```sh

```

## Launch

```sh
cd "$MY_BUTT" && . .venv/bin/activate && python3 kick_butt.py
```
