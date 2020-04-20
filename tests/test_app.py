import json
from unittest.mock import patch

import pytest
from geocoder.address_view import Address
from geocoder.app import server
from geocoder.db_worker import DbWorker
from geocoder.point_viev import OsmPoint


@pytest.fixture()
def client():
    with server.test_client() as client:
        yield client


@pytest.fixture()
def point():
    return OsmPoint(1.0, 2.0)


@pytest.mark.parametrize('point', (None, OsmPoint(1.0, 2.0)))
@patch.object(DbWorker, 'get_coordinates')
def test_get_address_coordinate(mock, client, point):
    mock.return_value = point
    response = client.get('/geocoder/api/v1.0/get_coord/City/Street/Number')
    data = json.loads(response.get_data())
    assert response.status_code == 200
    if point is None:
        assert data['Attention'] == 'This address does not exist in data base'
    else:
        assert data['Coordinates']['Latitude'] == point.latitude
        assert data['Coordinates']['Longitude'] == point.longitude


@pytest.mark.parametrize('address', (None, Address('Ленина', '1', 'Екатеринбург', '')))
@patch.object(DbWorker, 'get_address')
def test_get_coordinate_address(mock, client, address):
    mock.return_value = address
    response = client.get('/geocoder/api/v1.0/get_addr/latitude/longitude')
    data = json.loads(response.get_data())
    assert response.status_code == 200
    if address is None:
        assert (
            data['Error'] == 'This address does not exist or you coordinate incorrect'
        )
    else:
        assert data['Address']['City'] == address.city
        assert data['Address']['Street'] == address.street
        assert data['Address']['Number'] == address.number
