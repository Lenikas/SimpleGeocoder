import numpy


class Geometry:
    @staticmethod
    def find_centroid(coordinates, vertices_number):
        """Функция для поиска центра масс по набору координат"""
        xs = coordinates[:, 0]
        ys = coordinates[:, 1]
        centroid = numpy.zeros(2, dtype=numpy.float64)
        area = 0
        for index in range(vertices_number - 1):
            area += 0.5 * (xs[index] * ys[index + 1] - xs[index + 1] * ys[index])

        if area == 0.0:
            centroid[0] = 0
            centroid[1] = 0
            return centroid.tolist()

        area_factor = 1 / (6.0 * area)
        sum_x = 0
        sum_y = 0
        for index in range(vertices_number - 1):
            k = xs[index] * ys[index + 1] - xs[index + 1] * ys[index]
            sum_x += area_factor * (xs[index] + xs[index + 1]) * k
            sum_y += area_factor * (ys[index] + ys[index + 1]) * k

        centroid[0] = sum_x
        centroid[1] = sum_y
        return centroid.tolist()
