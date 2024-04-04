import pytest
import os
os.environ['FLASK_ENV'] = 'test'

from inf349 import app
from models import *


@pytest.fixture
def client():
    app.testing = True

    with app.test_client() as client:
        yield client
    

def test_get_products(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json['products'] is not None


def test_post_order(client):
    test_data = {
        'product': {
            'id': 1,
            'quantity': 2
        }
    }

    response = client.post('/order', json=test_data)

    assert response.status_code == 302 
    assert 'order' in response.headers['Location']  


def test_get_order(client):
    response = client.get('/order/1')

    assert response.status_code == 200
    assert response.json['order'] is not None


def test_put_order(client):
    test_data = {
        'order': {
            'shipping_information': {
                'country': 'Canada',
                'address': '123 Main St',
                'postal_code': 'A1A 1A1',
                'city': 'Montreal',
                'province': 'QC'
            },
            'email': 'test@example.com'
        }
    }

    response = client.put('/order/1', json=test_data)

    assert response.status_code == 200
    assert response.json['order'] is not None
    assert response.json['order']['shipping_information']['country'] == 'Canada'


def test_invalid_put_order(client):
    response = client.put('/order/999', json={})

    assert response.status_code == 404
    assert 'errors' in response.json
