import re


class Address:
    """Класс для внутреннего представления адреса"""

    def __init__(self, street, number, city, references=None):
        self.street = street
        self.number = number
        self.references = references
        self.city = city

    @property
    def street(self):
        return self._address

    @street.setter
    def street(self, address):
        words = [
            r'улица',
            'проспект',
            r'бульвар',
            r'переулок',
            r'проезд',
        ]
        for t in words:
            index = re.search(r'{}'.format(t), address)
            if index is not None:
                self._address = address.replace(t, '').strip()
                return
        self._address = address
