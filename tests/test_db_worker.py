import pathlib

import pytest
from final_project.db_structure import AddressToCoordinates, Base, create_session, engine
from final_project.db_worker import DbWorker
from final_project.osm_parser import OsmParser


@pytest.fixture(autouse=True)
def init_db(parser):
    Base.metadata.create_all(engine)
    DbWorker.prepare_db(parser)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture()
def parser():
    return OsmParser(pathlib.Path(__file__).parent / 'test_data/test_data.osm', [])


def test_prepare_db():
    with create_session() as session:
        data = session.query(AddressToCoordinates).all()
        assert data is not None
        assert len(data) > 0


def test_prepare_coordinates_bad_address():
    with create_session() as session:
        result = DbWorker.prepare_coordinates('None', 'None', 0, session)
        assert result is None


def test_prepare_coordinates():
    with create_session() as session:
        result = DbWorker.prepare_coordinates('Екатеринбург', 'Попова', 6, session)
        assert result[0][0] is not None
        assert result[0][1] is not None


def test_get_coordinates():
    result = DbWorker.get_coordinates('Екатеринбург', 'Попова', '6')
    assert result.latitude is not None
    assert result.longitude is not None


def test_get_address():
    coordinates = DbWorker.get_coordinates('Екатеринбург', 'Попова', '6')
    result = DbWorker.get_address(str(coordinates.latitude), str(coordinates.longitude))
    assert result.street == 'Попова'
    assert result.number == '6'
