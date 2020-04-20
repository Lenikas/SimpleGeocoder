import pytest
from geocoder.address_view import Address


@pytest.fixture()
def address():
    return Address('проспект Ленина', '52', 'Екатеринбург', '1 2 3')


def test_init_address(address):
    assert address.city == 'Екатеринбург'
    assert address.street == 'Ленина'
    assert address.number == '52'
    assert address.links == '1 2 3'
