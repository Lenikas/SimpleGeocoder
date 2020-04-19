import argparse
import os

from geocoder.db_create import create_db, create_finish


def input_console_data():
    """"Функция осуществляет парсинг аргументов при консольном запуске"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--file',
        type=str,
        help='Если хотите осуществить ввод данных через файл - используйте это',
    )
    parser.add_argument(
        '--make_base',
        type=bool,
        help='Если нет базы данных и Вы хотите создать - введите --make_base true '
        'если хотите создать базу данных(без неё не будет работать поиск координат)',
    )
    parser.add_argument('--city', type=str, help='Название города')
    parser.add_argument('--street', type=str, help='Название улицы')
    parser.add_argument('--house_number', type=str, help='Номер дома')
    namespace = parser.parse_args()
    if namespace.make_base is not None:
        path = os.path.join('./data', 'Ekaterinburg.osm')
        try:
            # BuildingFinder.finder(path, False)
            create_db(path)
            create_finish()
        except FileNotFoundError:
            print('загрузите базу OSM!')
        return (None,)
    return namespace.city, namespace.street, namespace.house_number
