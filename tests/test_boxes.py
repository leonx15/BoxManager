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


def test_get_item_by_code(client, register, login, app):
    register('codeuser')
    login('codeuser')
    client.post('/add_box', data={'name': 'BoxCode'})
    with app.app_context():
        box = Box.query.filter_by(name='BoxCode').first()
    client.post(
        f'/box/{box.id}/add_item',
        data={'name': 'ItemCode', 'description': 'desc', 'quantity': 1, 'ean_code': '111'},
    )
    response = client.get('/api/items/111')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'ItemCode'
    assert data['ean_code'] == '111'
    assert data['box_id'] == box.id


def test_get_item_by_code_not_found(client, register, login, app):
    """A logged-in user should receive 404 JSON when code does not exist."""
    register('missing')
    login('missing')
    client.post('/add_box', data={'name': 'EmptyBox'})
    with app.app_context():
        box = Box.query.filter_by(name='EmptyBox').first()
    # Add a different item code
    client.post(
        f'/box/{box.id}/add_item',
        data={'name': 'ItemX', 'description': 'd', 'quantity': 1, 'ean_code': '999'},
    )
    response = client.get('/api/items/does_not_exist')
    assert response.status_code == 404
    assert response.get_json() == {"error": "Item not found"}


def test_get_item_by_code_requires_login(client):
    response = client.get('/api/items/somecode')
    assert response.status_code == 401


def test_low_stock_items_requires_login(client):
    response = client.get('/low_stock_items')
    assert response.status_code == 401


def test_low_stock_items_view(client, register, login, app):
    register('lowuser')
    login('lowuser')
    client.post('/add_box', data={'name': 'StockBox'})
    with app.app_context():
        box = Box.query.filter_by(name='StockBox').first()
    client.post(
        f'/box/{box.id}/add_item',
        data={'name': 'AlmostGone', 'description': 'd', 'quantity': 1},
    )
    client.post(
        f'/box/{box.id}/add_item',
        data={'name': 'Plenty', 'description': 'd', 'quantity': 3},
    )
    response = client.get('/low_stock_items')
    assert response.status_code == 200
    assert b'AlmostGone' in response.data
    assert b'Plenty' not in response.data
