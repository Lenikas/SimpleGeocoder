import pathlib
import re
from typing import Any, Union

import numpy
from geocoder.address_view import Address
from geocoder.db_structure import (
    AddressToCoordinates,
    AddressToPoints,
    PointToCoordinate,
    create_session,
)
from geocoder.geometry import find_centroid
from geocoder.osm_parser import OsmParser
from geocoder.point_viev import OsmPoint


class DbWorker:
    @staticmethod
    def prepare_db(parser: OsmParser) -> None:
        """Наполняем базу данных"""
        with create_session() as session:
            with open(str(parser.path), encoding='utf-8') as f:
                current_city = 'Екатеринбург'
                for string in f:
                    string = string.lstrip()[:-1]
                    parser.buffer.append(string)

                    if re.match(r'<node id="', string) is not None:
                        point_data = parser.extract_coordinates_osm(string)
                        if point_data is not None:
                            session.add(
                                PointToCoordinate(
                                    point_data.link,
                                    point_data.latitude,
                                    point_data.longitude,
                                )
                            )

                    elif re.match(r'<tag k="addr:street" v="', string) is not None:
                        address_data = parser.extract_address_osm(string, current_city)
                        if address_data is not None:
                            session.add(
                                AddressToPoints(
                                    address_data.city,
                                    address_data.street,
                                    address_data.number,
                                    address_data.links,
                                )
                            )

                    if len(parser.buffer) == 40:
                        parser.buffer.pop(0)

                session.commit()
                for item in session.query(AddressToPoints).all():
                    coordinates_data = DbWorker.prepare_coordinates(
                        item.city, item.street, item.number, session
                    )
                    point = find_centroid(coordinates_data, len(coordinates_data))
                    session.add(
                        AddressToCoordinates(item.id, point.latitude, point.longitude)
                    )

    @staticmethod
    def prepare_coordinates(city: str, street: str, number: int, session: Any) -> Any:
        """Считаем координаты для адреса"""
        coordinates = []

        item = (
            session.query(AddressToPoints)
            .filter(AddressToPoints.city == city)
            .filter(AddressToPoints.street == street)
            .filter(AddressToPoints.number == number)
            .first()
        )
        if item is None:
            return None
        links = getattr(item, 'links')
        list_links = []
        for link in links.split():
            list_links.append(int(link))
        for i in list_links:
            item_coord = (
                session.query(PointToCoordinate)
                .filter(PointToCoordinate.link == i)
                .first()
            )
            latitude = getattr(item_coord, 'latitude')
            longitude = getattr(item_coord, 'longitude')
            coordinates.append([latitude, longitude])
        coordinates = numpy.array(coordinates)
        return coordinates

    @staticmethod
    def get_coordinates(city: str, street: str, number: str) -> Union[OsmPoint, None]:
        """Получаем координаты по адресу"""
        with create_session() as session:
            item = (
                session.query(AddressToPoints)
                .filter(AddressToPoints.city == city)
                .filter(AddressToPoints.street == street)
                .filter(AddressToPoints.number == number)
                .first()
            )

            if item is None:
                return None

            address_id = getattr(item, 'id')

            coordinates = (
                session.query(AddressToCoordinates)
                .filter(AddressToCoordinates.address_id == address_id)
                .first()
            )
            latitude = getattr(coordinates, 'latitude')
            longitude = getattr(coordinates, 'longitude')
            return OsmPoint(latitude, longitude)

    @staticmethod
    def get_address(latitude: str, longitude: str) -> Union[Address, None]:
        """Получаем адрес по координатам"""
        try:
            latitude_f = float(latitude)
            longitude_f = float(longitude)
        except TypeError:
            return None

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

            address = (
                session.query(AddressToPoints)
                .filter(AddressToPoints.id == address_id)
                .first()
            )

            city = getattr(address, 'city')
            street = getattr(address, 'street')
            number = getattr(address, 'number')
            return Address(street, number, city, '')

    @staticmethod
    def create_db() -> None:
        """Подготавливаем базу для работы"""
        path = pathlib.Path(__file__).cwd() / 'data/Ekaterinburg.osm'
        try:
            parser = OsmParser(path, [])
            DbWorker.prepare_db(parser)
        except FileNotFoundError:
            print('Загрузите базу OSM!')
