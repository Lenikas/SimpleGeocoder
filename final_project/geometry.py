import numpy
from final_project.point_viev import OsmPoint


def find_centroid(coordinates: numpy.array, vertices_number: int) -> OsmPoint:
    """Функция для поиска центра масс по набору координат"""
    xs = coordinates[:, 0]
    ys = coordinates[:, 1]
    area = 0
    for index in range(vertices_number - 1):
        area += 0.5 * (xs[index] * ys[index + 1] - xs[index + 1] * ys[index])

    if area == 0.0:
        return OsmPoint(0.0, 0.0)

    area_factor = 1 / (6.0 * area)
    sum_x = 0
    sum_y = 0
    for index in range(vertices_number - 1):
        k = xs[index] * ys[index + 1] - xs[index + 1] * ys[index]
        sum_x += area_factor * (xs[index] + xs[index + 1]) * k
        sum_y += area_factor * (ys[index] + ys[index + 1]) * k

    return OsmPoint(sum_x, sum_y)
