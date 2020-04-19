import pathlib
import re
from typing import List, Union, Any

from geocoder.address_view import Address
from geocoder.point_viev import Point


class OsmParser:
    """Методы для разбора osm данных"""
    def __init__(self, filename: pathlib.Path, buffer: List[str]):
        self.file_name = filename
        self.buffer = buffer

    @staticmethod
    def extract_coordinates_osm(data: str) -> Any:
        """Для каждой точки извлекаем широту и долготу"""
        s = re.findall(r'[0-9]{2}.[0-9]+', data)
        coordinates = [int(s[0]), float(s[6]), float(s[7])]
        return coordinates[0], coordinates[1], coordinates[2]

    def extract_address_osm(
        self, points: List[str], street: str, city: str, buffer_position: int
    ) -> Union[Address, None]:
        """Извлекаем номер дома и его точки """
        house_number = None
        for i in range(buffer_position, len(self.buffer)):
            if re.match(r'<tag k="addr:housenumber" v=', self.buffer[i]) is not None:
                house_number = self.buffer[i][29:-3]
                continue
            if re.match(r'<tag k="addr:city" v=', self.buffer[i]) is not None:
                city = self.buffer[i][22:-3].capitalize()
            if re.match(r'<nd ref="', self.buffer[i]) is not None:
                points.append(self.buffer[i][9:-3])
        if house_number is not None:
            build = Address(street, house_number, city, ' '.join(points))
            return build
        return None

    def get_address_osm(self, data: str, city: str) -> Union[Address, None]:
        """Собираем адрес из данных осм формата"""
        buffer_position = 0
        is_house = False
        for buffer_position in range(len(self.buffer) - 1, -1, -1):
            if re.match(r'<way id="', self.buffer[buffer_position]) is not None:
                is_house = True
                break
        if is_house:
            points: List[str] = []
            street = data[24:-3]
            address = self.extract_address_osm(points, street, city, buffer_position)
            return address
        return None

    def process_point_data(self, string: str) -> Union[Point, None]:
        """Обрабатываем входную строку c данными о точке из базы osm"""
        if re.match(r'<node id="', string) is not None:
            (point, latitude, longitude,) = self.extract_coordinates_osm(string)
            return Point(point, latitude, longitude)
        return None

    def process_address_data(
        self, string: str, current_city: str
    ) -> Union[Address, None]:
        """Обрабатываем входную строку c адресом из базы osm"""
        if re.match(r'<tag k="addr:street" v="', string) is not None:
            address = self.get_address_osm(string, current_city)
            return address
        return None
