from geocoder.argument_parser import input_console_data
from geocoder.db_create import calculate_coordinates
from geocoder.app import server


def main():
    data = input_console_data()
    if len(data) == 1:
        exit()
    city, street, house_number = data
    if city is None or street is None or house_number is None:
        city = input('Введите населённый пункт: ')
        street = input('Введите улицу/проспект/переулок/бульвар: ')
        house_number = input('Введите номер дома: ')
    coordinates = calculate_coordinates(city, street, house_number)
    try:
        result = (
            'Населённый пункт: {}\nУлица/проспект/переулок/бульвар: {}\nНомер дома: {}'
            '\nДолгота: {}\nШирота: {}'
        ).format(city, street, house_number, coordinates[0], coordinates[1])
        print(result)
    except TypeError:
        pass


if __name__ == '__main__':
    #main()
    server.run(debug=True)
