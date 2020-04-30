import logging
from typing import Any, Union

from final_project.db_utils.db_worker import DbWorker
from final_project.view_utils.address_view import Address
from flask import Flask, jsonify, make_response, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

server = Flask(__name__)
auth = HTTPBasicAuth()
logging.basicConfig(
    filename='logs.txt',
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s - %(message)s',
)


@auth.verify_password
def get_password(username: str, password: Any) -> Union[str, bool]:
    user_password = DbWorker.get_password(username)
    if user_password is None:
        return False
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
            400,
        )
    return jsonify({'Successful registration': {'username': username}}), 200


@server.route('/geocoder/api/v1.0/get_coord/', methods=['GET'])
def get_address_coordinate() -> Any:
    """Обработка запроса в формате get_coord/?city=city&street=street&number=number """
    city = request.args.get('city')
    street = request.args.get('street')
    number = request.args.get('number')

    if city is None or street is None or number is None:
        return (
            jsonify(
                {'Error': 'Bad request, give full address with city, street and number'}
            ),
            400,
        )

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


@server.route('/geocoder/api/v1.0/get_addr/', methods=['GET'])
def get_coordinate_address() -> Any:
    """Обработка запроса в формате get_addr/?latitude=latitude&longitude=longitude """
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')

    if latitude is None or longitude is None:
        return (
            jsonify({'Error': 'Bad request, give latitude and longitude of address'}),
            400,
        )

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


@server.route('/geocoder/api/v1.0/<username>/save_address/', methods=['POST'])
# @auth.login_required
def save_address(username: str) -> Any:
    if (
        not request.json
        or 'city' not in request.json
        or 'street' not in request.json
        or 'number' not in request.json
    ):
        return (
            jsonify(
                {'Error': 'Invalid data, please give city street and number of address'}
            ),
            400,
        )

    city = request.json.get('city')
    street = request.json.get('street')
    number = request.json.get('number')
    address = Address(street, number, city, '')
    if DbWorker.add_data_to_user(username, address):
        return jsonify({'Success': 'Address will be add to your storage'}), 200

    return jsonify({'Error': 'This address does not exist id database'}), 400


@server.route('/geocoder/api/v1.0/<username>/get_save_addr/', methods=['GET'])
# @auth.login_required
def get_save_addr(username: str) -> Any:
    data = DbWorker.get_user_data(username)
    dict_data = {}
    for item in data:
        key = (
            f'City: {item[0].city}, Street: {item[0].street}, Number: {item[0].number}'
        )
        value = f'latitude: {item[1].latitude}, longitude: {item[1].longitude}'
        dict_data[key] = value
    return jsonify({'Information': 'abc'}), 200
