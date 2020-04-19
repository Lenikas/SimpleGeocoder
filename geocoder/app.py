from flask import Flask, jsonify
from geocoder.db_create import get_address, get_coordinates

server = Flask(__name__)


@server.route('/geocoder/api/v1.0/get_coord/<city>/<street>/<number>', methods=['GET'])
def get_address_coordinate(city: str, street: str, number: str):
    coordinates = get_coordinates(city, street, number)
    if coordinates is None:
        return jsonify({'Attention': 'This address does not exist in data base'}), 200

    if coordinates[0] == coordinates[1] == 0:
        return jsonify({'Error': 'Can not calculate coordinates, sorry'}), 200

    latitude = coordinates[0]
    longitude = coordinates[1]
    response = {
        'City': city,
        'Street': street,
        'Number': number,
        'Latitude': latitude,
        'Longitude': longitude,
    }
    return jsonify({'Response': response}), 200


@server.route('/geocoder/api/v1.0/get_addr/<latitude>/<longitude>', methods=['GET'])
def get_coordinate_address(latitude, longitude):
    address = get_address(latitude, longitude)
    if address is None:
        return jsonify({'Attention': 'This address does not exist in data base'}), 200

    response = {
        'City': address.city,
        'Street': address.address,
        'Number': address.house_number,
        'Latitude': latitude,
        'Longitude': longitude,
    }
    return jsonify({'Response': response}), 200
