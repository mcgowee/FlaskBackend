# app/tests/test_routes.py
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_hello(client):
    rv = client.get('/api/hello')
    assert rv.status_code == 200
    assert b'Hello, World!' in rv.data
