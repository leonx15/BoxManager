from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from ..models import User, Box, Item
from .. import db, login_manager

# Blueprint setup
boxes = Blueprint('boxes', __name__)


@boxes.route('/add_box', methods=['GET'])
@login_required
def add_box():  # pragma: no cover
    session.permanent = True  # pragma: no cover
    return render_template('add_box.html', owner_id=current_user.id)  # pragma: no cover


@boxes.route('/add_box', methods=['POST'])
@login_required
def handle_add_box():
    box_name = request.form['name']
    description = request.form.get('description', '')

    if not box_name:
        flash('Box name is required.', 'error')
        return redirect(url_for('boxes.add_box'))

    # Create a new Box instance, using current_user.id directly for the owner_id
    new_box = Box(name=box_name, description=description, owner_id=current_user.id)

    db.session.add(new_box)
    db.session.commit()

    flash('Box added successfully!', 'success')
    return redirect(url_for('boxes.add_box_success'))


@boxes.route('/add_box_success')
@login_required
def add_box_success():  # pragma: no cover
    session.permanent = True  # pragma: no cover
    # This route confirms the box was added. You can customize as needed.
    return "Box added successfully!"  # pragma: no cover


@boxes.route('/my_boxes')
@login_required
def my_boxes():  # pragma: no cover
    session.permanent = True  # pragma: no cover
    # Query the database for boxes created by the currently logged-in user
    user_boxes = Box.query.filter_by(owner_id=current_user.id).all()  # pragma: no cover

    # Pass the list of boxes to the template
    return render_template('my_boxes.html', boxes=user_boxes)  # pragma: no cover


@boxes.route('/box/<int:box_id>')
@login_required
def box_details(box_id):
    session.permanent = True
    box = Box.query.get_or_404(box_id)
    if box.owner_id != current_user.id:
        flash('You do not have access to this box.', 'error')
        return redirect(url_for('boxes.my_boxes'))
    return render_template('box_details.html', box=box)


@boxes.route('/box/<int:box_id>/add_item', methods=['GET', 'POST'])
@login_required
def add_item(box_id):
    session.permanent = True
    box = Box.query.get_or_404(box_id)
    if box.owner_id != current_user.id:
        flash('You do not have access to this box.', 'error')
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        quantity = request.form.get('quantity', 1, type=int)  # Default quantity to 1 if not provided
        ean_code = request.form.get('ean_code') or None
        new_item = Item(name=name, description=description, quantity=quantity, box_id=box_id, ean_code=ean_code)
        db.session.add(new_item)
        db.session.commit()
        flash('Item added successfully!', 'success')
        return redirect(url_for('boxes.box_details', box_id=box_id))
    return render_template('add_item.html', box=box)  # pragma: no cover


@boxes.route('/scanner')
@login_required
def scanner():
    """Display barcode/QR code scanner page."""
    session.permanent = True
    return render_template('scanners.html')


@boxes.route('/api/items/<string:ean_code>')
@login_required
def get_item_by_code(ean_code):
    """Return item details as JSON for the given EAN code."""
    item = (
        Item.query.join(Box)
        .filter(Item.ean_code == ean_code, Box.owner_id == current_user.id)
        .first()
    )
    if not item:
        return {"error": "Item not found"}, 404
    return {
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "ean_code": item.ean_code,
        "quantity": item.quantity,
        "box_id": item.box_id,
    }
