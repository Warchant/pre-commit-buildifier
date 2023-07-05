import argparse
import logging
import os
import platform
import shutil
import stat
import subprocess
import sys
from io import UnsupportedOperation

import requests

logging.root.name = "pre-commit-buildifier"


def chmod(file):
    assert os.path.exists(file), file
    st = os.stat(file)
    os.chmod(file, st.st_mode | stat.S_IEXEC)


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

        # make it executable
        chmod(local_file_path)
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


def get_arch():
    arch = platform.machine()
    if arch == "x86_64":
        arch = "amd64"
    return arch


def get_name(version):
    o = get_os()
    name = f"buildifier_{o}_{version}"
    if o == "windows":
        name += ".exe"
    return name


# https://github.com/bazelbuild/buildtools/releases/download/5.1.0/buildozer-windows-amd64.exe
def get_buildifier(args):
    if not args.path and not args.version:
        raise ValueError("--path or --version should be set")

    if args.path:
        path = shutil.which("buildifier")
        if not path or not os.path.exists(path) or not os.path.isfile(path):
            return None

        logging.info(f"Found buildififer in PATH: {path}")
        chmod(path)
        return path

    if not args.version:
        raise ValueError("version cannot be empty")

    basedir = os.path.dirname(__file__)
    name = get_name(args.version)
    bpath = os.path.join(basedir, name)
    if not os.path.exists(bpath):
        # buildifier of this version does ot exist
        logging.info(f"{name} does not exist. Downloading...")

        _os = get_os()
        _arch = get_arch()
        ext = ""
        if _os == "windows":
            ext = ".exe"

        url = f"https://github.com/bazelbuild/buildtools/releases/download/{args.version}/buildifier-{_os}-{_arch}{ext}"
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
    parser.add_argument(
        "--path",
        default=False,
        action="store_true",
        help="Search for buildifier in PATH (default: False)",
    )
    parser.add_argument("file", nargs="+", action="store")
    args, extra = parser.parse_known_args()

    buildifier_bin = get_buildifier(args)
    subprocess.check_call([buildifier_bin, "-lint=fix"] + extra + args.file)


if __name__ == "__main__":
    main()
