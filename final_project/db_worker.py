import pathlib
import re
from typing import Any, List, Tuple, Union

import numpy
from final_project.db_structure import (
    AddressToCoordinates,
    AddressToPoints,
    PointToCoordinate,
    User,
    UsersData,
    create_session,
)
from final_project.geometry_utils.geometry import find_centroid
from final_project.osm_parser.osm_parser import OsmParser
from final_project.view_utils.address_view import Address
from final_project.view_utils.point_viev import OsmPoint
from sqlalchemy.exc import IntegrityError


class DbWorker:
    """Класс для подготовки базы данных для геокодирования и взаимодействия с этими данными"""

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
    def add_user(username: str, password: str) -> Union[None, str]:
        try:
            with create_session() as session:
                session.add(User(username, password))
            return username
        except IntegrityError:
            return None

    @staticmethod
    def get_password(username: str) -> Union[str, None]:
        with create_session() as session:
            user = session.query(User).filter(User.username == username).first()
            if user is None:
                return None
            return getattr(user, 'password',)

    @staticmethod
    def add_data_to_user(username: str, address: Address) -> bool:
        with create_session() as session:
            user_record = session.query(User).filter(User.username == username).first()
            address_record = (
                session.query(AddressToPoints)
                .filter(AddressToPoints.street == address.street)
                .filter(AddressToPoints.number == address.number)
                .first()
            )

            if address_record is None:
                return False

            session.add(UsersData(user_record.id, address_record.id))
            return True

    @staticmethod
    def get_user_data(username: str) -> List[Tuple[Address, OsmPoint]]:
        data_with_coordinate = []
        with create_session() as session:
            user_record = session.query(User).filter(User.username == username).first()
            user_addresses = (
                session.query(UsersData)
                .filter(UsersData.user_id == user_record.id)
                .all()
            )
            for item in user_addresses:
                data = (
                    session.query(AddressToPoints)
                    .filter(AddressToPoints.id == item.id)
                    .first()
                )
                coordinates = (
                    session.query(AddressToCoordinates)
                    .filter(AddressToCoordinates.address_id == item.id)
                    .first()
                )
                data_with_coordinate.append(
                    (
                        Address(data.street, data.number, data.city, ''),
                        OsmPoint(coordinates.latitude, coordinates.longitude),
                    )
                )

        return data_with_coordinate

    @staticmethod
    def create_db() -> None:
        """Подготавливаем базу для работы"""
        path = pathlib.Path(__file__).cwd() / 'data/Ekaterinburg.osm'
        try:
            parser = OsmParser(path, [])
            DbWorker.prepare_db(parser)
        except FileNotFoundError:
            print('Загрузите базу OSM!')
