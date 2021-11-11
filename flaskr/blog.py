from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

from flaskr.db import get_db
from datetime import date

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
    return render_template('create.html')


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

@bp.route("/buy",methods=["POST","GET"])
def buy():
    sales = "*" if request.form.get("sales") == "" else request.form.get("sales")
    customer = "*" if request.form.get("customer") == "" else request.form.get("customer")
    vin = "*" if request.form.get("vin") == "" else request.form.get("vin")
    error = None

    db = get_db()
    sales = db.execute(
        "SELECT e_id FROM Employees WHERE name = '{0}'".format(sales)
    ).fetchall()

    customer = db.execute(
        "SELECT c_id FROM customers WHERE name = '{0}'".format(customer)
    ).fetchall()

    vin = db.execute(
        "SELECT vin,MSRP FROM Inventory WHERE vin = '{0}'".format(vin)
    ).fetchall()

    if len(sales) == 0:
        error = f"Sales name is not valid!"

    if len(customer) == 0:
        error = f"customer name is not valid!"
    
    if len(vin) == 0:
        error = f"vin is not valid!"
    
    in_stock = db.execute(
        "SELECT * FROM Stored_in WHERE vin = '{0}'".format(vin[0][0])
    ).fetchall()
    if len(in_stock) == 0:
        error = f"the car is out of stock!"
    
    discount = db.execute(
        "SELECT discount_rate FROM Manager WHERE e_id = '{0}'".format(sales[0][0])
    ).fetchall()
    discountRate = 1 if len(discount) == 0 else (1-discount[0][0])

    orderNum = db.execute(
        "SELECT order_number FROM Ord"
    ).fetchall()[-1][0]+1

    print (discountRate)
    print (vin[0][1])

    if error is None:
        db.execute(
            "INSERT INTO ord(order_number, price, order_date, vin) VALUES ({0},{1},'{2}', '{3}')".format(orderNum, vin[0][1]*discountRate, date.today(), vin[0][0])
        )
        db.execute(
            "INSERT INTO Purchase(c_id, order_number) VALUES ({0},{1})".format(customer[0][0],orderNum)
        )
        db.execute(
            "INSERT INTO Sell(e_id, order_number) VALUES ({0},{1})".format(sales[0][0],orderNum)
        )
        return "Order Success!"
    return error

@bp.route("/sale",methods=["POST","GET"])
def sale():
    db = get_db()
    order = -1 if request.form.get("order") == "" else int(request.form.get("order"))
    error = None

    print (order)
    if order == -1:
        error = f"Order number is  invalid!"
    
    if error is None:
        db.execute(
            "DELETE FROM Purchase WHERE order_number= {0}".format(order)
        )
        db.execute(
            "DELETE FROM Sell WHERE order_number= {0}".format(order)
        )
        db.execute(
            "DELETE FROM ord WHERE order_number= {0}".format(order)
        )
        return "Order Success!"
    return error