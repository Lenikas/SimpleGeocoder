import json
from base64 import b64encode
from unittest.mock import patch

import pytest
from final_project.app import server
from final_project.db_worker import DbWorker
from final_project.view_utils.address_view import Address
from final_project.view_utils.point_viev import OsmPoint


@pytest.fixture()
def client():
    with server.test_client() as client:
        yield client


@pytest.fixture()
def point():
    return OsmPoint(1.0, 2.0)


@pytest.fixture()
def address():
    return Address('Попова', '6', 'Екатеринбург', '')


@pytest.fixture()
def login():
    return 'login'


@pytest.fixture()
def password():
    return 'password'


@pytest.fixture(autouse=True)
def header(login, password):
    token = b64encode(f'{login}:{password}'.encode()).decode()
    return {'Authorization': f'Basic {token}'}


def test_add_user(client):
    response = client.post(
        '/geocoder/api/v1.0/registration',
        data=json.dumps({'username': 'abc', 'password': 'qwerty'}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert data['Successful registration'] == {'username': 'abc'}


def test_add_user_invalid_data(client):
    response = client.post(
        '/geocoder/api/v1.0/registration',
        data=json.dumps({'username': 'abc'}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['ERROR'] == 'Invalid data, please give username and password'


@pytest.mark.parametrize('point', (None, OsmPoint(1.0, 2.0)))
@patch.object(DbWorker, 'get_coordinates')
def test_get_address_coordinate(mock, client, point):
    mock.return_value = point
    response = client.get(
        '/geocoder/api/v1.0/get_coord/?city=city&street=street&number=number'
    )
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
    response = client.get(
        '/geocoder/api/v1.0/get_addr/?latitude=latitude&longitude=longitude'
    )
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


@pytest.mark.parametrize(
    'request_url',
    (
        '/geocoder/api/v1.0/get_coord/?city=city&street=street',
        '/geocoder/api/v1.0/get_addr/?latitude=latitude',
    ),
)
def test_bad_request(client, request_url):
    response = client.get(request_url)
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['Error'] is not None


@pytest.mark.parametrize('mock_value', (True, False))
@patch.object(DbWorker, 'add_data_to_user')
def test_save_address(mock, client, header, mock_value):
    client.post(
        '/geocoder/api/v1.0/registration/?username=login&password=qwerty',
        content_type='application/json',
    )
    mock.return_value = mock_value
    response = client.post(
        '/geocoder/api/v1.0/login/save_address/?city=city&street=street&number=number',
        headers=header,
        data=json.dumps({'city': 'city', 'street': 'street', 'number': 'number'}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    if mock_value:
        assert response.status_code == 200
        assert data['Success'] == 'Address will be add to your storage'
    else:
        assert response.status_code == 400
        assert data['Error'] == 'This address does not exist id database'


def test_save_address_bad_request(client, header):
    response = client.post(
        '/geocoder/api/v1.0/login/save_address/?city=city&street=street&number=number',
        headers=header,
        data=json.dumps({'city': 'city'}),
        content_type='application/json',
    )
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert (
        data['Error'] == 'Invalid data, please give city street and number of address'
    )


@patch.object(DbWorker, 'get_user_data')
def test_get_save_addr(mock, client, point, address):
    mock.return_value = [(address, point)]
    response = client.get('/geocoder/api/v1.0/login/get_save_addr/?',)
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert data['Information'] is not None
