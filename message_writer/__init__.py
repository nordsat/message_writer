import json

import yaml
from posttroll.message import datetime_encoder
from posttroll.subscriber import create_subscriber_from_dict_config
from pyresample.area_config import load_area
from contextlib import closing
import argparse

def write_message_to_file(msg, filename, area_file):
    with open(filename, "w") as fd:
        json.dump([message_to_json(area_file, msg)],
                  fd, default=datetime_encoder)


def message_to_json(area_file, msg):
    area = load_area(area_file, msg.data["area"])
    return {"uri": msg.data["uri"],
            "layer": msg.data["product"],
            "start_time": msg.data["start_time"],
            "area_extent": area.area_extent,
            "proj4": area.proj_str
            }


def append_message_to_file(msg, filename, area_file):
    try:
        with open(filename) as fd:
            data = json.load(fd)
    except FileNotFoundError:
        data = []
    data.append(message_to_json(area_file, msg))
    with open(filename, "w") as fd:
        json.dump(data, fd, default=datetime_encoder)

def subscribe_and_write(filename, area_file, subscriber_settings):
    with closing(create_subscriber_from_dict_config(subscriber_settings)) as sub:
        for message in sub.recv():
            append_message_to_file(message, filename, area_file)


def read_config(yaml_file):
    with open(yaml_file) as fd:
        data = yaml.safe_load(fd.read())
    return data['filename'], data["area_file"], data["subscriber_config"]


def main(args=None):
    """Main script."""
    parsed_args = parse_args(args=args)
    subscribe_and_write(*read_config(parsed_args.config_file))

def parse_args(args=None):
    """Parse commandline arguments."""
    parser = argparse.ArgumentParser("Message writer",
                                     description="Write message into a json file for wms")
    parser.add_argument("config_file",
                        help="The configuration file to run on.")
    return parser.parse_args(args)
