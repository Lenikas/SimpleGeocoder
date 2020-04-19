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
    __tablename__ = 'address_to_points'

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    city = sa.Column(sa.String, nullable=False)
    street = sa.Column(sa.String, nullable=False)
    number = sa.Column(sa.String, nullable=False)
    points = sa.Column(sa.String, nullable=False)

    def __init__(self, city: str, street: str, number: str, points: Any):
        self.city = city
        self.street = street
        self.number = number
        self.points = points


class PointToCoordinate(Base):
    __tablename__ = 'point_to_coordinate'

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    point = sa.Column(sa.Integer, nullable=False)
    latitude = sa.Column(sa.REAL, nullable=False)
    longitude = sa.Column(sa.REAL, nullable=False)

    def __init__(self, point: int, latitude: float, longitude: float):
        self.point = point
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


Base.metadata.create_all(engine)
