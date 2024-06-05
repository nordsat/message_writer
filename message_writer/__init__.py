"""Test the message writer.

Example config::

  subscriber_settings:
    nameserver: false
    addresses: ipc://bla
  filename: /data/list_of_files.json
  area_file: /some/where/areas.yaml

"""

import argparse
import json
import pathlib
import logging
from contextlib import closing

import yaml
from posttroll.subscriber import create_subscriber_from_dict_config
from pyresample.area_config import load_area
from trollsift.parser import Parser

_LOGGER = logging.getLogger("message-writer")
logging.basicConfig(level=logging.INFO)


def datetime_encoder(obj):
    """Encodes datetimes into iso format."""
    try:
        return obj.isoformat() + "Z"
    except AttributeError as exc:
        raise TypeError(repr(obj) + " is not JSON serializable") from exc


def write_message_to_file(msg, filename, area_file):
    """Write a message to a json file."""
    with open(filename, "w") as fd:
        json.dump([message_to_json(area_file, msg.data)],
                  fd, default=datetime_encoder)


def message_to_json(area_file, info):
    """Write a message to json format."""
    area = load_area(area_file, info["area"])
    return dict_from_info(info, area)


def append_message_to_file(msg, filename, area_file):
    """Append a message to a file (existing or not)."""
    try:
        with open(filename) as fd:
            data = json.load(fd)
    except FileNotFoundError:
        data = []
    data.append(message_to_json(area_file, msg.data))
    with open(filename, "w") as fd:
        json.dump(data, fd, default=datetime_encoder)


def subscribe_and_write(filename, area_file, subscriber_settings):
    """Subscribe and write."""
    with closing(create_subscriber_from_dict_config(subscriber_settings)) as sub:
        for message in sub.recv():
            append_message_to_file(message, filename, area_file)


def read_config(yaml_file):
    """Read a config file."""
    with open(yaml_file) as fd:
        data = yaml.safe_load(fd.read())
    return data


def main(args=None):
    """Main script."""
    parsed_args = parse_args(args=args)
    config = read_config(parsed_args.config_file)
    _LOGGER.info(config)
    subscribe_and_write(config["filename"],
                        config["area_file"],
                        config["subscriber_settings"])

def parse_args(args=None):
    """Parse commandline arguments."""
    parser = argparse.ArgumentParser("Message writer",
                                     description="Write message into a json file for wms")
    parser.add_argument("config_file",
                        help="The configuration file to run on.")
    parser.add_argument("files", nargs="*", action="store")
    return parser.parse_args(args)


def create_list_from_files(filename, area_file, filepattern, list_of_files):
    """Create list from provided files."""
    parser = Parser(filepattern)
    data = []
    for f in list_of_files:
        info = parser.parse(f)
        info["uri"] = f
        area = load_area(area_file, info["area"])
        data.append(dict_from_info(info, area))
    with open(filename, "w") as fd:
        json.dump(data, fd, default=datetime_encoder)


def dict_from_info(info, area):
    """Create the required dict from info."""
    return {"uri": info["uri"],
            "layer": info["product"],
            "start_time": info["start_time"],
            "area_extent": area.area_extent,
            "proj4": area.proj_str
            }


def files_to_list(args=None):
    """Script for files to list."""
    parsed_args = parse_args(args=args)
    config = read_config(parsed_args.config_file)
    _LOGGER.info(config)
    full_paths = []
    for path in parsed_args.files:
        full_paths = [str(p) for p in pathlib.Path(path).iterdir() if p.is_file()]
    create_list_from_files(config["filename"], config["area_file"], config["filepattern"], full_paths)
