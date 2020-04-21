import logging
from typing import Any

from final_project.db_worker import DbWorker
from flask import Flask, jsonify

server = Flask(__name__)
logging.basicConfig(
    filename='logs.txt',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    # datefmt='%d-%b-%y %H:%M:%S',
)


@server.route(
    '/final_project/api/v1.0/get_coord/<city>/<street>/<number>', methods=['GET']
)
def get_address_coordinate(city: str, street: str, number: str) -> Any:
    coordinates = DbWorker.get_coordinates(city, street, number)
    if coordinates is None:
        return jsonify({'Attention': 'This address does not exist in data base'}), 200

    if coordinates.latitude == coordinates.longitude == 0:
        return jsonify({'Error': 'Can not calculate coordinates, sorry'}), 200

    response = {
        'Latitude': coordinates.latitude,
        'Longitude': coordinates.longitude,
    }
    return jsonify({'Coordinates': response}), 200


@server.route(
    '/final_project/api/v1.0/get_addr/<latitude>/<longitude>', methods=['GET']
)
def get_coordinate_address(latitude: str, longitude: str) -> Any:
    address = DbWorker.get_address(latitude, longitude)
    if address is None:
        return (
            jsonify(
                {'Error': 'This address does not exist or you coordinate incorrect'}
            ),
            200,
        )

    response = {
        'City': address.city,
        'Street': address.street,
        'Number': address.number,
    }
    return jsonify({'Address': response}), 200
