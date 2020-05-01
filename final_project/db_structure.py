from contextlib import contextmanager
from typing import Any

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = sa.create_engine('sqlite:///geocoder_base.sqlite')
Session = sessionmaker(bind=engine)
Base: Any = declarative_base()


@contextmanager
def create_session(**kwargs: Any) -> Any:
    new_session = Session(**kwargs)
    try:
        yield new_session
        new_session.commit()
    except Exception:
        new_session.rollback()
        raise
    finally:
        new_session.close()


class AddressToPoints(Base):
    """Вспомогательная таблица сырых данных"""

    __tablename__ = 'address_to_points'

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    city = sa.Column(sa.String, nullable=False)
    street = sa.Column(sa.String, nullable=False)
    number = sa.Column(sa.String, nullable=False)
    links = sa.Column(sa.String, nullable=False)

    def __init__(self, city: str, street: str, number: str, links: Any):
        self.city = city
        self.street = street
        self.number = number
        self.links = links


class PointToCoordinate(Base):
    __tablename__ = 'point_to_coordinate'

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    link = sa.Column(sa.Integer, nullable=False)
    latitude = sa.Column(sa.REAL, nullable=False)
    longitude = sa.Column(sa.REAL, nullable=False)

    def __init__(self, point: int, latitude: float, longitude: float):
        self.link = point
        self.longitude = longitude
        self.latitude = latitude


class AddressToCoordinates(Base):
    __tablename__ = 'address_to_coordinates'

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    address_id = sa.Column(
        sa.Integer, sa.ForeignKey(AddressToPoints.id), nullable=False
    )
    latitude = sa.Column(sa.REAL)
    longitude = sa.Column(sa.REAL)

    def __init__(self, address_id: int, latitude: float, longitude: float):
        self.address_id = address_id
        self.longitude = longitude
        self.latitude = latitude


class User(Base):
    __tablename__ = 'user'

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    username = sa.Column(sa.String, nullable=False, unique=True)
    password = sa.Column(sa.String, nullable=False, unique=True)

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


class UsersData(Base):
    __tablename__ = 'usersData'

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(User.id), nullable=False)
    data_id = sa.Column(
        sa.Integer, sa.ForeignKey(AddressToCoordinates.id), nullable=False
    )

    def __init__(self, user_id: int, data_id: int):
        self.user_id = user_id
        self.data_id = data_id


Base.metadata.create_all(engine)
