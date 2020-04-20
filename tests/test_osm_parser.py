import pathlib

import pytest
from geocoder.osm_parser import OsmParser


@pytest.fixture()
def parser():
    return OsmParser(pathlib.Path(__file__).parent / 'test_data/test_data.osm', [])


@pytest.fixture()
def data_osm(parser):
    with open(str(parser.path), 'r') as f:
        data = f.read()
        return data


@pytest.fixture()
def data_coordinate():
    path = str(pathlib.Path(__file__).parent / 'test_data/test_coordinate_data.txt')
    with open(path, 'r') as f:
        return f.read()


@pytest.fixture()
def data_address():
    path = str(pathlib.Path(__file__).parent / 'test_data/test_address_data.txt')
    with open(path, 'r') as f:
        return f.read()


def test_init_parser(parser):
    assert parser.path is not None
    assert parser.buffer == []


def test_extract_coordinates_osm(parser, data_coordinate):
    result = parser.extract_coordinates_osm(data_coordinate)
    assert result.link == 176197027
    assert result.latitude == 56.8389083
    assert result.longitude == 60.5902521


def test_get_address_osm(parser, data_address):
    pass
