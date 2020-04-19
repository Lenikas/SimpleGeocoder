import re

import numpy
from geocoder.building import Building
from geocoder.db_structure import (
    AddressToCoordinates,
    AddressToPoints,
    PointToCoordinate,
    create_session,
)
from geocoder.geometry import Geometry


def extract_coordinates_osm(data: str):
    s = re.findall(r'[0-9]{2}.[0-9]+', data)
    coordinates = [int(s[0]), float(s[6]), float(s[7])]
    return coordinates[0], coordinates[1], coordinates[2]


def extract_address_one_way(buffer, references, house_number, street, city, j):
    for i in range(j, len(buffer)):
        if re.match(r'<tag k="addr:housenumber" v=', buffer[i]) is not None:
            house_number = buffer[i][29:-3]
            continue
        if re.match(r'<tag k="addr:city" v=', buffer[i]) is not None:
            city = buffer[i][22:-3].capitalize()
        if re.match(r'<nd ref="', buffer[i]) is not None:
            references.append(buffer[i][9:-3])
    if house_number is not None:
        build = Building(street, house_number, city, ' '.join(references))
        return build
    return None


def extract_address_two_way(buffer, references, house_number, street, city, j):
    for i in range(j, len(buffer)):
        if re.match(r'<tag k="addr:street"', buffer[i]) is not None:
            street = buffer[i][24:-3]
            continue
        if re.match(r'<nd ref="', buffer[i]) is not None:
            references.append(buffer[i][9:-3])
        if re.match(r'<tag k="addr:city" v=', buffer[i]) is not None:
            city = buffer[i][22:-3].capitalize()
    if street is not None:
        build = Building(street, house_number, city, ' '.join(references))
        return build
    return None


def a(session, data, buffer, current_city, counter):
    if re.match(r'<tag k="addr:street" v="', data) is not None:
        j = 0
        is_house = False
        for j in range(len(buffer) - 1, -1, -1):
            if re.match(r'<way id="', buffer[j]) is not None:
                is_house = True
                break
        if is_house:
            references = []
            street = data[24:-3]
            house_number = None
            city = current_city
            build = extract_address_one_way(
                buffer, references, house_number, street, city, j
            )
            if build is None:
                counter = 5
            else:
                references = ' '.join(build.references)
                session.add(
                    AddressToPoints(
                        build.city, build.address, build.house_number, build.references,
                    )
                )


def b(session, data, buffer, current_city, counter):
    if re.match(r'<tag k="addr:housenumber" v=', data) is not None:
        counter = 0
        j = 0
        is_house = False
        for j in range(len(buffer) - 1, -1, -1):
            if re.match(r'<way id="', buffer[j]) is not None:
                is_house = True
                break
        if is_house:
            references = []
            house_number = data[29:-3]
            city = current_city
            street = None
            build = extract_address_two_way(
                buffer, references, house_number, street, city, j
            )
            if build is not None:
                references = ' '.join(build.references)
                session.add(
                    AddressToPoints(
                        build.city, build.address, build.house_number, build.references,
                    )
                )


def create_db(file_name):
    with create_session() as session:
        try:
            with open(file_name, encoding='utf-8') as f:
                buffer = []
                counter = 0
                current_city = 'Екатеринбург'
                for string in f:
                    string = string.lstrip()[:-1]
                    buffer.append(string)
                    if counter <= 0:
                        if re.match(r'<node id="', string) is not None:
                            try:
                                point, latitude, longitude = extract_coordinates_osm(
                                    string
                                )
                                session.add(
                                    PointToCoordinate(point, latitude, longitude)
                                )
                            except IndexError:
                                continue
                        a(session, string, buffer, current_city, counter)

                    elif counter > 0:
                        counter -= 1
                        b(session, string, buffer, current_city, counter)
                    if len(buffer) == 40:
                        buffer.pop(0)
        except FileNotFoundError:
            raise FileNotFoundError('База OSM не загружена!')


def create_finish():
    with create_session() as session:
        for item in session.query(AddressToPoints).all():
            coordinates = calculate_coordinates(item.city, item.street, item.number)
            session.add(AddressToCoordinates(item.id, coordinates[0], coordinates[1]))


def calculate_coordinates(city, address, number_of_house):
    """Функция ищет координаты по заданному адресу"""
    coordinates = []
    print(address, number_of_house)
    with create_session() as session:
        item = (
            session.query(AddressToPoints)
            .filter(AddressToPoints.city == city)
            .filter(AddressToPoints.street == address)
            .filter(AddressToPoints.number == number_of_house)
            .first()
        )
        if item is None:
            return None
        points = getattr(item, 'points')
        links = points.split()
        res = []
        for link in links:
            res.append(int(link))
        for i in res:
            item_coord = (
                session.query(PointToCoordinate)
                .filter(PointToCoordinate.point == i)
                .first()
            )
            latitude = getattr(item_coord, 'latitude')
            longitude = getattr(item_coord, 'longitude')
            coordinates.append([latitude, longitude])
        coordinates = numpy.array(coordinates)
        return Geometry.find_centroid(coordinates, len(coordinates))


def get_coordinates(city: str, street: str, number: str):
    with create_session() as session:
        address_id = getattr(
            session.query(AddressToPoints)
            .filter(AddressToPoints.city == city)
            .filter(AddressToPoints.street == street)
            .filter(AddressToPoints.number == number)
            .first(),
            'id',
        )
        coordinates = (
            session.query(AddressToCoordinates)
            .filter(AddressToCoordinates.address_id == address_id)
            .first()
        )
        latitude = getattr(coordinates, 'latitude')
        longitude = getattr(coordinates, 'longitude')
        return [latitude, longitude]


def get_address(latitude, longitude):
    latitude_f = float(latitude)
    longitude_f = float(longitude)
    with create_session() as session:
        item = (
            session.query(AddressToCoordinates)
            .filter(AddressToCoordinates.latitude == latitude_f)
            .filter(AddressToCoordinates.longitude == longitude_f)
            .first()
        )
        if item is None:
            return None

        address_id = getattr(item, 'address_id')

        address = session.query(AddressToPoints).filter(AddressToPoints.id == address_id).first()

        city = getattr(address, 'city')
        street = getattr(address, 'street')
        number = getattr(address, 'number')
        return Building(street, number, city)
