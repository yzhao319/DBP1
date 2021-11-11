from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

from flaskr.db import get_db
import json


bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    return render_template('welcome.html')

@bp.route('/orders')
def orders():
    db = get_db()
    orders = db.execute(
        'SELECT c.order_number, c.name as sName, customers.name as cName, c.price, c.order_date, c.vin FROM Customers,'
        '(SELECT Purchase.c_id, s.order_number, s.name, s.price, s.order_date, s.vin from Purchase, '
        '(SELECT e.order_number, name, e.price, e.order_date, e.vin from employees,'
        '(SELECT e_id, ord.order_number, ord.price, ord.order_date, ord.vin FROM ord, sell WHERE  sell.order_number=ord.order_number) as e'
        ' WHERE e.e_id = employees.e_id) as s WHERE s.order_number = Purchase.order_number) as c WHERE Customers.c_id = c.c_id'
    ).fetchall()
    return render_template('order.html', orders=orders)


@bp.route('/inventory')
def inventory():
    db = get_db()
    inventories = db.execute(
        'SELECT * FROM Inventory'
    ).fetchall()
    return render_template('inventory.html', inventories=inventories)

@bp.route('/create')
def create():
    db = get_db()
    inventories = db.execute(
        'SELECT * FROM Stored_in'
    ).fetchall()
    return render_template('create.html', inventories=inventories)


@bp.route("/search",methods=["POST","GET"])
def search():
    color = "*" if request.form.get("color") == "" else request.form.get("color")
    make = "*" if request.form.get("make") == "" else request.form.get("make")
    db = get_db()
    inventories = db.execute(
        "SELECT * FROM Inventory WHERE (Inventory.color = '{0}' AND Inventory.make = '{1}')".format(color,make) 
    ).fetchall()
    result = [dict(row) for row in inventories]
    myDict = {}
    myDict["res"] = result
    return myDict

@bp.route("/reset",methods=["POST","GET"])
def reset():
    db = get_db()
    inventories = db.execute(
        "SELECT * FROM Inventory"
    ).fetchall()
    result = [dict(row) for row in inventories]
    myDict = {}
    myDict["res"] = result
    return myDict