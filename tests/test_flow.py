import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import boxmanager
from boxmanager import create_app, db
from boxmanager.models import User, Box, Item

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


def register(client, username, password='pw'):
    return client.post('/register', data={'username': username, 'password': password})


def login(client, username, password='pw', follow_redirects=False):
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=follow_redirects)


def test_login_success_and_home(client):
    register(client, 'charlie')
    response = login(client, 'charlie', follow_redirects=True)
    assert b'Hello, charlie!' in response.data


def test_login_invalid_credentials(client):
    register(client, 'dave')
    response = login(client, 'dave', password='wrong', follow_redirects=True)
    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert ('message', 'Invalid username or password') in sess.get('_flashes', [])


def test_home_redirects_when_logged_out(client):
    response = client.get('/')
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/login')


def test_load_user_invalid_uuid(app):
    from boxmanager.blueprints.routes_main import load_user
    with app.app_context():
        assert load_user('not-a-uuid') is None


def test_protected_route_requires_login(client):
    response = client.get('/my_boxes')
    assert response.status_code == 401


def test_add_box_and_item_flow(app, client):
    register(client, 'owner')
    login(client, 'owner')
    client.post('/add_box', data={'name': 'Box1', 'description': 'desc'})
    with app.app_context():
        box = Box.query.filter_by(name='Box1').first()
        assert box is not None
    client.post(f'/box/{box.id}/add_item', data={'name': 'Item1', 'description': 'item', 'quantity': 2})
    response = client.get(f'/box/{box.id}')
    assert b'Item1' in response.data


def test_add_box_requires_name(app, client):
    register(client, 'owner2')
    login(client, 'owner2')
    response = client.post('/add_box', data={'name': '', 'description': 'd'})
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/add_box')
    with client.session_transaction() as sess:
        messages = [msg for cat, msg in sess.get('_flashes', [])]
        assert 'Box name is required.' in messages
    with app.app_context():
        assert Box.query.count() == 0


def test_box_details_access_control(app, client):
    register(client, 'user1')
    login(client, 'user1')
    client.post('/add_box', data={'name': 'Box2'})
    with app.app_context():
        box = Box.query.filter_by(name='Box2').first()
    client.get('/logout')
    register(client, 'user2')
    login(client, 'user2')
    response = client.get(f'/box/{box.id}')
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/my_boxes')
    with client.session_transaction() as sess:
        messages = [msg for category, msg in sess.get('_flashes', [])]
        assert 'You do not have access to this box.' in messages


def test_add_item_access_control(app, client):
    register(client, 'owner3')
    login(client, 'owner3')
    client.post('/add_box', data={'name': 'Shared'})
    with app.app_context():
        box = Box.query.filter_by(name='Shared').first()
    client.get('/logout')
    register(client, 'intruder')
    login(client, 'intruder')
    response = client.post(f'/box/{box.id}/add_item', data={'name': 'Bad'}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/')
    with client.session_transaction() as sess:
        messages = [msg for _c, msg in sess.get('_flashes', [])]
        assert 'You do not have access to this box.' in messages

