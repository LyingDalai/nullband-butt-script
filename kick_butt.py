import configparser
import subprocess
import time
from pathlib import Path
import shutil
from urllib.error import URLError, HTTPError
from urllib.request import urlopen

"""
1. Load user's local ~/.buttrc as the base, fails if not found
2. Fetch Nullband’s latest config
3. Merge the remote “nullband” section into the user config
4. Save a patched config at ~/.nullband_butt.conf
5. Launch BUTT
6. Tile streams automatically
"""


# ----------------------------
# Settings
# ----------------------------
CONFIG_URL = "https://nullband.org/transmit/config"
USER_BUTTRC = Path.home() / ".buttrc"
OUTPUT_PATH = Path.home() / ".nullband_butt.conf"
STREAM_DURATION = 45 * 60  # 45 minutes
PRE_FETCH = 60  # pre-fetch 1 minute before end

BUTT_EXEC = shutil.which("butt") or "/Applications/BUTT.app/Contents/MacOS/butt"

if not Path(BUTT_EXEC).exists():
    raise FileNotFoundError("BUTT executable not found. Please install BUTT.")
    
# ----------------------------
# Helper functions
# ----------------------------
def load_base_config() -> configparser.ConfigParser:
    """Load user's .buttrc if exists, otherwise return a fresh config."""
    config = configparser.ConfigParser()
    config.optionxform = str  # preserve case # type: ignore

    if not USER_BUTTRC.exists():
        raise FileNotFoundError(
            f"Couldn't find user's local butt conf file at\n\n{USER_BUTTRC}\n\n"
            "Please make sure you adjust your desired settings and save your config in butt first:"
            "\nSettings > Main > Configuration > Save"
        )

    config.read(USER_BUTTRC)
    print(f"Loaded user config from {USER_BUTTRC}")
    return config


def fetch_and_patch_config(output_path: Path):
    """
    Fetch the latest nullband config, patch device and bitrate settings,
    and save locally, starting from user's base .buttrc.
    """
    # Fetch remote config
    try:
        with urlopen(CONFIG_URL) as resp:
            remote_text = resp.read().decode("utf-8")
    except HTTPError as e:
        raise RuntimeError(f"HTTP error: {e.code}") from e
    except URLError as e:
        raise RuntimeError(f"Connection error: {e.reason}") from e    
        # Load remote config
    remote_config = configparser.ConfigParser()
    remote_config.optionxform = str  # type: ignore
    remote_config.read_string(remote_text)

    # Start from base (user) config
    config = load_base_config()
    if not config:
        config = remote_config
    else:
        # Merge/override nullband section
        if not config.has_section("nullband"):
            config.add_section("nullband")
        # Copy each key from the fetched remote config
        if "nullband" in remote_config:
            for key, value in remote_config["nullband"].items():
                config["nullband"][key] = value

    # Save patched config
    with output_path.open("w") as f:
        config.write(f)

    print(f"Patched config saved to {output_path}")


def start_butt(config_path: Path):
    """Launch BUTT with the given config file."""
    return subprocess.Popen([BUTT_EXEC, "-c", str(config_path)])


# ----------------------------
# Tiling loop
# ----------------------------
def stream_tile():
    proc = None
    print("Launching the script, simply press Ctrl+C to stop.")
    while True:
        # Fetch & patch config
        print("Fetching latest config from nullband...")
        fetch_and_patch_config(OUTPUT_PATH)

        # Launch new stream
        print("Launching butt...")
        new_proc = start_butt(OUTPUT_PATH)
        print("  > Butt launched, hit the play button to start broadcasting.")

        # Pre-fetch next config 1 minute before end
        if proc:
            time.sleep(STREAM_DURATION - PRE_FETCH)
            print("Fetching new config from nullband...")
            fetch_and_patch_config(OUTPUT_PATH)
            print("Launching new butt...")
            next_proc = start_butt(OUTPUT_PATH)
            print("Next stream pre-fetched: hit play button to start.")

            # Wait remaining 1 min
            time.sleep(PRE_FETCH)
            proc.terminate()
            proc.wait()
            print("Previous segment ended, continuing with next stream.")
            proc = next_proc
        else:
            # First iteration, wait full duration
            time.sleep(STREAM_DURATION)
            proc = new_proc


# ----------------------------
# Entry point
# ----------------------------
if __name__ == "__main__":
    stream_tile()
