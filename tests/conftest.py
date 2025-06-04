import os
import sys
import pytest

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import boxmanager
from boxmanager import create_app


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


@pytest.fixture
def register(client):
    def _register(username, password='pw'):
        return client.post('/register', data={'username': username, 'password': password})
    return _register


@pytest.fixture
def login(client):
    def _login(username, password='pw', follow_redirects=False):
        return client.post('/login', data={'username': username, 'password': password}, follow_redirects=follow_redirects)
    return _login
