def test_register_new_user_redirects_to_login(client, register):
    response = register('alice')
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/login')


def test_register_existing_user_shows_error(client, register):
    register('bob')
    response = register('bob')
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/register')
    with client.session_transaction() as sess:
        assert ('message', 'Username already exists') in sess.get('_flashes', [])


def test_login_success_and_home(client, register, login):
    register('charlie')
    response = login('charlie', follow_redirects=True)
    assert b'Hello, charlie!' in response.data


def test_login_invalid_credentials(client, register, login):
    register('dave')
    response = login('dave', password='wrong', follow_redirects=True)
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
