import logging
from typing import Any, Union

from final_project.db_worker import DbWorker
from flask import Flask, jsonify, make_response, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

server = Flask(__name__)
auth = HTTPBasicAuth()
logging.basicConfig(
    filename='logs.txt',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
)


@auth.verify_password
def get_password(username: str, password: Any) -> Union[str, bool]:
    user_password = DbWorker.get_password(username)
    # check none
    return check_password_hash(user_password, password)


@auth.error_handler
def unauthorized() -> Any:
    return make_response(jsonify({'ERROR': 'Unauthorized access'}), 401)


@server.route('/geocoder/api/v1.0/registration', methods=['POST'])
def add_user() -> Any:
    if (
        not request.json
        or 'username' not in request.json
        or 'password' not in request.json
    ):
        return (
            jsonify({'ERROR': 'Invalid data, please give username and password'}),
            400,
        )

    username = request.json.get('username')
    password = generate_password_hash(request.json.get('password'))

    if DbWorker.add_user(username, password) is None:
        return (
            jsonify({'Warning': 'User with the same name or password does exist'}),
            403,
        )
    return jsonify({'Successful registration': {'username': username}}), 200


@server.route('/geocoder/api/v1.0/get_coord/<city>/<street>/<number>', methods=['GET'])
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


@server.route('/geocoder/api/v1.0/get_addr/<latitude>/<longitude>', methods=['GET'])
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
