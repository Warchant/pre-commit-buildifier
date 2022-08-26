import argparse
import logging
import os
import subprocess
import sys
from io import UnsupportedOperation

import requests

logging.root.name = "pre-commit-buildifier"


def download_file(url, local_file_path):
    # Send HTTP GET request to server and attempt to receive a response
    r = requests.get(url)
    if r.status_code != 200:
        logging.critical(f"Cannot download {url}: code {r.status_code}")
        sys.exit(1)

    # Write the file contents in the response to a file specified by local_file_path
    try:
        with open(local_file_path, "wb") as local_file:
            for chunk in r.iter_content(chunk_size=2**12):
                local_file.write(chunk)
    except Exception as e:
        logging.critical(f"Cannot write to a file {local_file_path}: {e}")
        sys.exit(1)


def get_os():
    from sys import platform

    if platform == "linux" or platform == "linux2":
        return "linux"
    elif platform == "darwin":
        return "darwin"
    elif platform == "win32":
        return "windows"
    raise UnsupportedOperation(f"Unsupported os: {platform}")


def get_name(version):
    o = get_os()
    name = f"buildifier_{o}_{version}"
    if o == "windows":
        name += ".exe"
    return name


# https://github.com/bazelbuild/buildtools/releases/download/5.1.0/buildozer-windows-amd64.exe
def get_buildifier(version):
    if not version:
        raise ValueError("version cannot be empty")

    basedir = os.path.dirname(__file__)
    name = get_name(version)
    bpath = os.path.join(basedir, name)
    if not os.path.exists(bpath):
        # buildifier of this version does ot exist
        logging.info(f"{name} does not exist. Downloading...")
        url = f"https://github.com/bazelbuild/buildtools/releases/download/{version}/buildifier-{get_os()}-amd64.exe"
        download_file(url, bpath)
    return bpath


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version",
        default="5.1.0",
        type=str,
        action="store",
        help="Buildifier version",
    )
    parser.add_argument("file", nargs="+", action="store")
    args, extra = parser.parse_known_args()

    buildifier_bin = get_buildifier(args.version)
    subprocess.check_call([buildifier_bin, "-lint=fix"] + extra + args.file)
