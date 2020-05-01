import re


class Address:
    """Класс для внутреннего представления адреса"""

    def __init__(self, street: str, number: str, city: str, links: str) -> None:
        if links is None:
            links = []
        self.street = street
        self.number = number
        self.links = links
        self.city = city

    @property
    def street(self) -> str:
        return self._address

    @street.setter
    def street(self, address: str) -> None:
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
