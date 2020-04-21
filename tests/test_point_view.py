import pytest
from final_project.point_viev import OsmPoint


@pytest.fixture()
def point():
    return OsmPoint(0.0, 1.0, 123)


def test_init_point(point):
    assert point.link == 123
    assert point.latitude == 0.0
    assert point.longitude == 1.0
