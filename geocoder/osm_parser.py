import pathlib
import re

from geocoder.address_view import Address
from geocoder.point_viev import Point


class OsmParser:
    def __init__(self, filename: pathlib.Path, buffer, counter):
        self.file_name = filename
        self.buffer = buffer
        self.counter = counter

    @staticmethod
    def extract_coordinates_osm(data: str):
        """Для каждой точки извлекаем широту и долготу"""
        s = re.findall(r'[0-9]{2}.[0-9]+', data)
        coordinates = [int(s[0]), float(s[6]), float(s[7])]
        return coordinates[0], coordinates[1], coordinates[2]

    def extract_address_one_osm_format(self, references, street, city, buffer_position):
        """Извлекаем номер дома и его точки """
        house_number = None
        for i in range(buffer_position, len(self.buffer)):
            if re.match(r'<tag k="addr:housenumber" v=', self.buffer[i]) is not None:
                house_number = self.buffer[i][29:-3]
                continue
            if re.match(r'<tag k="addr:city" v=', self.buffer[i]) is not None:
                city = self.buffer[i][22:-3].capitalize()
            if re.match(r'<nd ref="', self.buffer[i]) is not None:
                references.append(self.buffer[i][9:-3])
        if house_number is not None:
            build = Address(street, house_number, city, ' '.join(references))
            return build
        return None

    def extract_address_two_osm_format(
        self, references, house_number, city, buffer_position
    ):
        """Извлекаем улицу и точки для нее"""
        street = None
        for i in range(buffer_position, len(self.buffer)):
            if re.match(r'<tag k="addr:street"', self.buffer[i]) is not None:
                street = self.buffer[i][24:-3]
                continue
            if re.match(r'<nd ref="', self.buffer[i]) is not None:
                references.append(self.buffer[i][9:-3])
            if re.match(r'<tag k="addr:city" v=', self.buffer[i]) is not None:
                city = self.buffer[i][22:-3].capitalize()
        if street is not None:
            build = Address(street, house_number, city, ' '.join(references))
            return build
        return None

    def get_address_one_osm_format(self, data, city):
        """Собираем адрес из данных осм формата"""
        buffer_position = 0
        is_house = False
        for buffer_position in range(len(self.buffer) - 1, -1, -1):
            if re.match(r'<way id="', self.buffer[buffer_position]) is not None:
                is_house = True
                break
        if is_house:
            points = []
            street = data[24:-3]
            build = self.extract_address_one_osm_format(
                points, street, city, buffer_position
            )
            if build is None:
                self.counter = 5
            return build
        return None

    def get_address_two_osm_format(self, data, city):
        self.counter = 0
        buffer_position = 0
        is_house = False
        for buffer_position in range(len(self.buffer) - 1, -1, -1):
            if re.match(r'<way id="', self.buffer[buffer_position]) is not None:
                is_house = True
                break
        if is_house:
            points = []
            house_number = data[29:-3]
            build = self.extract_address_two_osm_format(
                points, house_number, city, buffer_position
            )
            return build
        return None

    def process_point_data(self, string):
        """Обрабатываем входную строку c данными о точке из базы osm"""
        if self.counter <= 0:
            if re.match(r'<node id="', string) is not None:
                (point, latitude, longitude,) = self.extract_coordinates_osm(string)
                return Point(point, latitude, longitude)
        return None

    def process_address_data(self, string, current_city):
        """Обрабатываем входную строку c адресом из базы osm"""
        if self.counter <= 0:
            if re.match(r'<tag k="addr:street" v="', string) is not None:
                build = self.get_address_one_osm_format(string, current_city)
                return build
        elif self.counter > 0:
            self.counter -= 1
            if re.match(r'<tag k="addr:housenumber" v=', string) is not None:
                build = self.get_address_two_osm_format(string, current_city)
                return build
        if len(self.buffer) == 40:
            self.buffer.pop(0)
        return None
