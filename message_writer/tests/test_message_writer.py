test_message = """pytroll://image/seviri_hrit file mraspaud@0c8caa669351 2023-05-22T10:59:20.391466 v1.01 application/json {"orig_platform_name": "MSG3", "service": "___", "start_time": "2023-05-22T10:45:00", "compression": "_", "platform_name": "Meteosat-10", "sensor": ["seviri"], "uri": "/mnt/output/20230522_1045_Meteosat-10_euro4_overview.tif", "uid": "20230522_1045_Meteosat-10_euro4_overview.tif", "product": "overview", "area": "euro4", "productname": "overview", "areaname": "euro4", "format": "tif"}"""

from message_writer import write_message_to_file, append_message_to_file, subscribe_and_write, read_config, main, create_list_from_files, files_to_list
from posttroll.message import Message
from posttroll.testing import patched_subscriber_recv
import json
import numpy as np
import os
import yaml
import pytest

area_content = """
euro4:
  description: Euro 4km area - Europe
  projection:
    proj: stere
    ellps: bessel
    lat_0: 90.0
    lon_0: 14.0
    lat_ts: 60.0
  shape:
    height: 1024
    width: 1024
  area_extent:
    lower_left_xy: [-2717181.7304994687, -5571048.14031214]
    upper_right_xy: [1378818.2695005313, -1475048.1403121399]
"""

@pytest.fixture
def area_file(tmp_path):
    area_file = tmp_path / "areas.yaml"
    with open(area_file, "w") as fd:
        fd.write(area_content)
    return area_file


@pytest.fixture
def filename(tmp_path):
    return tmp_path / "list_of_files.json"

def test_write_message_to_file(filename, area_file):
    msg = Message(rawstr=test_message)

    write_message_to_file(msg, filename, area_file)
    with open(filename, "r") as fd:
        data = json.load(fd)

    assert len(data) == 1
    info = data[0]
    assert info["uri"] == msg.data["uri"]
    assert info["layer"] == msg.data["product"]
    assert info["start_time"] == "2023-05-22T10:45:00"
    np.testing.assert_allclose(info["area_extent"], [-2717181.73, -5571048.14, 1378818.26, -1475048.14])
    assert set(info["proj4"].split()) == set("+proj=stere +lat_0=90 +lat_ts=60 +lon_0=14 +x_0=0 +y_0=0 +ellps=bessel +units=m +no_defs +type=crs".split())

def test_append_message_to_file(filename, area_file):
    msg = Message(rawstr=test_message)

    write_message_to_file(msg, filename, area_file)
    append_message_to_file(msg, filename, area_file)
    with open(filename, "r") as fd:
        data = json.load(fd)

    assert len(data) == 2


def test_subscribe_and_write(filename, area_file):
    subscriber_settings = dict(addresses="ipc://bla", nameserver=False)
    with patched_subscriber_recv([Message(rawstr=test_message)]):
        subscribe_and_write(filename, area_file, subscriber_settings)

    with open(filename, "r") as fd:
        data = json.load(fd)

    assert len(data) == 1

def test_config_reader(tmp_path, filename, area_file):
    """Test the config reader."""
    sub_config = dict(nameserver=False, addresses=["ipc://bla"])
    test_config = dict(subscriber_config=sub_config,
                       filename=os.fspath(filename),
                       area_file=os.fspath(area_file))
    yaml_file = tmp_path / "config.yaml"
    with open(yaml_file, "w") as fd:
        fd.write(yaml.dump(test_config))
    config = read_config(yaml_file)
    assert config["subscriber_config"] == sub_config
    assert config["area_file"] == os.fspath(area_file)
    assert config["filename"] == os.fspath(filename)


def test_main_crashes_when_config_missing():
    """Test that main crashes when config is missing."""
    with pytest.raises(SystemExit):
        main([])


def test_main_crashes_when_config_file_missing():
    """Test that main crashes when the config file is missing."""
    with pytest.raises(FileNotFoundError):
        main(["moose_config.yaml"])


list_of_files = """20230522_0930_Meteosat-10_euro4_airmass.tif
20230522_0930_Meteosat-10_euro4_natural_color.tif
20230522_0930_Meteosat-10_euro4_overview.tif
20230522_0945_Meteosat-10_euro4_airmass.tif
20230522_0945_Meteosat-10_euro4_natural_color.tif
20230522_0945_Meteosat-10_euro4_overview.tif
20230522_1000_Meteosat-10_euro4_airmass.tif
20230522_1000_Meteosat-10_euro4_natural_color.tif
20230522_1000_Meteosat-10_euro4_overview.tif
20230522_1015_Meteosat-10_euro4_airmass.tif
20230522_1015_Meteosat-10_euro4_natural_color.tif
20230522_1015_Meteosat-10_euro4_overview.tif
20230522_1030_Meteosat-10_euro4_airmass.tif
20230522_1030_Meteosat-10_euro4_natural_color.tif
20230522_1030_Meteosat-10_euro4_overview.tif
20230522_1045_Meteosat-10_euro4_airmass.tif
20230522_1045_Meteosat-10_euro4_natural_color.tif
20230522_1045_Meteosat-10_euro4_overview.tif
20230522_1100_Meteosat-10_euro4_airmass.tif
20230522_1100_Meteosat-10_euro4_natural_color.tif
20230522_1100_Meteosat-10_euro4_overview.tif
20230522_1115_Meteosat-10_euro4_airmass.tif
20230522_1115_Meteosat-10_euro4_natural_color.tif
20230522_1115_Meteosat-10_euro4_overview.tif
20230522_1130_Meteosat-10_euro4_airmass.tif
20230522_1130_Meteosat-10_euro4_natural_color.tif
20230522_1130_Meteosat-10_euro4_overview.tif
20230522_1145_Meteosat-10_euro4_airmass.tif
20230522_1145_Meteosat-10_euro4_natural_color.tif
20230522_1145_Meteosat-10_euro4_overview.tif
20230522_1200_Meteosat-10_euro4_airmass.tif
20230522_1200_Meteosat-10_euro4_natural_color.tif
20230522_1200_Meteosat-10_euro4_overview.tif
20230522_1215_Meteosat-10_euro4_airmass.tif
20230522_1215_Meteosat-10_euro4_natural_color.tif
20230522_1215_Meteosat-10_euro4_overview.tif"""

def test_create_list_from_files(filename, area_file):
    lof = list_of_files.split()
    filepattern = "{start_time:%Y%m%d_%H%M}_{platform_name}_{area}_{product}.tif"
    create_list_from_files(filename, area_file, filepattern, lof)
    with open(filename) as fd:
        data = json.load(fd)
    assert len(data) == 36

def test_files_to_list(tmp_path, filename, area_file):
    test_config = dict(filepattern="{start_time:%Y%m%d_%H%M}_{platform_name}_{area}_{product}.tif",
                       filename=os.fspath(filename),
                       area_file=os.fspath(area_file))
    yaml_file = tmp_path / "config.yaml"
    with open(yaml_file, "w") as fd:
        fd.write(yaml.dump(test_config))
    args = [os.fspath(yaml_file)]
    args.extend(list_of_files.split())
    files_to_list(args)
    with open(filename) as fd:
        data = json.load(fd)
    assert len(data) == 36
