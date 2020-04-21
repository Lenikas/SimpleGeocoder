import numpy
import pytest
from final_project.geometry import find_centroid


@pytest.mark.parametrize(
    'coordinates',
    (
        (
            numpy.array([[10, 10], [20, 20], [10, 20], [20, 10]]),
            [10.0, 3.333333333333332],
        ),
        (numpy.array([[0, 0], [0, 0], [0, 0], [0, 0]]), [0, 0]),
    ),
)
def test_centroid_finder(coordinates):
    result = find_centroid(coordinates[0], len(coordinates[0]))
    assert result.latitude == coordinates[1][0]
    assert result.longitude == coordinates[1][1]
