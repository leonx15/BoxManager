from boxmanager.models import Box


def test_add_box_and_item_flow(app, client, register, login):
    register('owner')
    login('owner')
    client.post('/add_box', data={'name': 'Box1', 'description': 'desc'})
    with app.app_context():
        box = Box.query.filter_by(name='Box1').first()
        assert box is not None
    client.post(f'/box/{box.id}/add_item', data={'name': 'Item1', 'description': 'item', 'quantity': 2})
    response = client.get(f'/box/{box.id}')
    assert b'Item1' in response.data


def test_add_box_requires_name(app, client, register, login):
    register('owner2')
    login('owner2')
    response = client.post('/add_box', data={'name': '', 'description': 'd'})
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/add_box')
    with client.session_transaction() as sess:
        messages = [msg for cat, msg in sess.get('_flashes', [])]
        assert 'Box name is required.' in messages
    with app.app_context():
        assert Box.query.count() == 0


def test_box_details_access_control(app, client, register, login):
    register('user1')
    login('user1')
    client.post('/add_box', data={'name': 'Box2'})
    with app.app_context():
        box = Box.query.filter_by(name='Box2').first()
    client.get('/logout')
    register('user2')
    login('user2')
    response = client.get(f'/box/{box.id}')
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/my_boxes')
    with client.session_transaction() as sess:
        messages = [msg for category, msg in sess.get('_flashes', [])]
        assert 'You do not have access to this box.' in messages


def test_add_item_access_control(app, client, register, login):
    register('owner3')
    login('owner3')
    client.post('/add_box', data={'name': 'Shared'})
    with app.app_context():
        box = Box.query.filter_by(name='Shared').first()
    client.get('/logout')
    register('intruder')
    login('intruder')
    response = client.post(f'/box/{box.id}/add_item', data={'name': 'Bad'}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/')
    with client.session_transaction() as sess:
        messages = [msg for _c, msg in sess.get('_flashes', [])]
        assert 'You do not have access to this box.' in messages


def test_scanner_requires_login(client):
    response = client.get('/scanner')
    assert response.status_code == 401


def test_scanner_route_logged_in(client, register, login):
    register('scanner')
    login('scanner')
    response = client.get('/scanner')
    assert response.status_code == 200
    assert b'Scan 1D/2D Code' in response.data
