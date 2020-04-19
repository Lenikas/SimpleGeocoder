import re


class Building:
    """Класс для внутреннего представления объектов"""

    def __init__(self, address, house_number, city, references=None):
        self.address = address
        self.house_number = house_number
        self.references = references
        self.city = city

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, address):
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
