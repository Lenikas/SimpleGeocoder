import pathlib

import pytest
from final_project.db_structure import (
    AddressToCoordinates,
    Base,
    create_session,
    engine,
)
from final_project.db_worker import DbWorker
from final_project.osm_parser.osm_parser import OsmParser
from final_project.view_utils.address_view import Address


@pytest.fixture(autouse=True)
def init_db(parser):
    Base.metadata.create_all(engine)
    DbWorker.prepare_db(parser)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture()
def parser():
    return OsmParser(pathlib.Path(__file__).parent / 'test_data/test_data.osm', [])


@pytest.fixture()
def address():
    return Address('Попова', '6', 'Екатеринбург', '')


def test_prepare_db():
    with create_session() as session:
        data = session.query(AddressToCoordinates).all()
        assert data is not None
        assert len(data) > 0


def test_prepare_coordinates_bad_address():
    with create_session() as session:
        result = DbWorker.prepare_coordinates('None', 'None', 0, session)
        assert result is None


def test_prepare_coordinates(address):
    with create_session() as session:
        result = DbWorker.prepare_coordinates(
            address.city, address.street, int(address.number), session
        )
        assert result[0][0] is not None
        assert result[0][1] is not None


def test_get_coordinates(address):
    result = DbWorker.get_coordinates(address.city, address.street, address.number)
    assert result.latitude is not None
    assert result.longitude is not None


def test_get_address(address):
    coordinates = DbWorker.get_coordinates(address.city, address.street, address.number)
    result = DbWorker.get_address(str(coordinates.latitude), str(coordinates.longitude))
    assert result.street == 'Попова'
    assert result.number == '6'


def test_add_user():
    result = DbWorker.add_user('username', 'password')
    assert result == 'username'


def test_add_data_to_user(address):
    DbWorker.add_user('username', 'password')
    result = DbWorker.add_data_to_user('username', address)
    assert result is True


def test_get_user_data(address):
    DbWorker.add_user('username', 'password')
    DbWorker.add_data_to_user('username', address)
    result = DbWorker.get_user_data('username')
    assert type(result) is list
    assert result[0][0].city == address.city
