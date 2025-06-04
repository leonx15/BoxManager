import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import boxmanager
from boxmanager import create_app, db

class TestConfig(boxmanager.Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'filesystem'
    SECRET_KEY = 'test'


@pytest.fixture
def app():
    original_config = boxmanager.Config
    boxmanager.Config = TestConfig
    app = create_app()
    yield app
    boxmanager.Config = original_config


@pytest.fixture
def client(app):
    return app.test_client()


def test_register_new_user_redirects_to_login(client):
    response = client.post('/register', data={'username': 'alice', 'password': 'pw'})
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/login')


def test_register_existing_user_shows_error(client):
    # First registration should succeed
    client.post('/register', data={'username': 'bob', 'password': 'pw'})
    # Second attempt with same username should trigger flash and redirect
    response = client.post('/register', data={'username': 'bob', 'password': 'pw'})
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/register')
    with client.session_transaction() as sess:
        assert ('message', 'Username already exists') in sess.get('_flashes', [])
