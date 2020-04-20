import pathlib
import re
from typing import List, Union

from geocoder.address_view import Address
from geocoder.point_viev import OsmPoint


class OsmParser:
    """Методы для разбора osm данных"""

    def __init__(self, file_path: pathlib.Path, buffer: List[str]):
        self.path = file_path
        self.buffer = buffer

    @staticmethod
    def extract_coordinates_osm(data: str) -> OsmPoint:
        """Для каждой точки извлекаем широту и долготу"""
        s = re.findall(r'[0-9]{2}.[0-9]+', data)
        coordinates = [int(s[0]), float(s[6]), float(s[7])]
        return OsmPoint(coordinates[1], coordinates[2], int(coordinates[0]))

    def prepare_address_osm(
        self, links: List[str], street: str, city: str, buffer_position: int
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
                links.append(self.buffer[i][9:-3])
        if house_number is not None:
            address = Address(street, house_number, city, ' '.join(links))
            return address
        return None

    def extract_address_osm(self, data: str, city: str) -> Union[Address, None]:
        """Собираем адрес из данных osm формата"""
        buffer_position = 0
        is_house = False
        for buffer_position in range(len(self.buffer) - 1, -1, -1):
            if re.match(r'<way id="', self.buffer[buffer_position]) is not None:
                is_house = True
                break
        if is_house:
            links: List[str] = []
            street = data[24:-3]
            address = self.prepare_address_osm(links, street, city, buffer_position)
            return address
        return None
