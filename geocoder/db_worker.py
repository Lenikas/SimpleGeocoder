import pathlib
from typing import Any, List, Union

import numpy
from geocoder.address_view import Address
from geocoder.db_structure import (
    AddressToCoordinates,
    AddressToPoints,
    PointToCoordinate,
    create_session,
)
from geocoder.geometry import Geometry
from geocoder.osm_parser import OsmParser


class DbWorker:
    @staticmethod
    def prepare_db(parser: OsmParser) -> None:
        """Наполняем базу данных"""
        with create_session() as session:
            with open(str(parser.file_name), encoding='utf-8') as f:
                current_city = 'Екатеринбург'
                for string in f:
                    string = string.lstrip()[:-1]
                    parser.buffer.append(string)

                    point_data = parser.process_point_data(string)
                    if point_data is not None:
                        session.add(
                            PointToCoordinate(
                                point_data.point,
                                point_data.latitude,
                                point_data.longitude,
                            )
                        )
                        continue
                    address_data = parser.process_address_data(string, current_city)
                    if address_data is not None:
                        session.add(
                            AddressToPoints(
                                address_data.city,
                                address_data.street,
                                address_data.number,
                                address_data.points,
                            )
                        )
                        continue
                session.commit()
            for item in session.query(AddressToPoints).all():
                coordinates = DbWorker.calculate_coordinates(
                    item.city, item.street, item.number
                )
                session.add(
                    AddressToCoordinates(item.id, coordinates[0], coordinates[1])
                )

    @staticmethod
    def calculate_coordinates(city: str, street: str, number_of_house: int) -> Any:
        """Считаем координаты для адреса"""
        coordinates = []
        with create_session() as session:
            item = (
                session.query(AddressToPoints)
                .filter(AddressToPoints.city == city)
                .filter(AddressToPoints.street == street)
                .filter(AddressToPoints.number == number_of_house)
                .first()
            )
            if item is None:
                return None
            points = getattr(item, 'points')
            res = []
            for link in points.split():
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

    @staticmethod
    def get_coordinates(
        city: str, street: str, number: str
    ) -> Union[List[float], None]:
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
            return [latitude, longitude]

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
