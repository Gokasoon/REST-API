from flask import Flask, jsonify, request, redirect, url_for, render_template
from models import *
import requests
import os
import sys


app = Flask(__name__)

db_name = os.environ.get('DB_NAME')
db_user = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASSWORD')
db_host = os.environ.get('DB_HOST')
db_port = os.environ.get('DB_PORT')

@app.cli.command()
def init_db():
    db = PostgresqlDatabase(
        database=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )

    db.connect()
    db.create_tables([Product, OrderItem, CreditCard, ShippingInformation, Order, Transaction], safe=True)
    OrderOrderItemThrough = OrderItem.orders.get_through_model()
    OrderOrderItemThrough.create_table()
    db.close()
    

@app.route('/', methods=['GET'])
def get_products():
    products = Product.select().dicts()
    return jsonify({"products": list(products)})
    

@app.route('/web', methods=['GET'])
def show_products():
    products = get_products().json['products']
    return render_template('products.html', products=products)
   


@app.route('/order', methods=['POST'])
def post_order():
    data = request.get_json()

    total_price = 0
    total_weight = 0

    if 'products' not in data and 'product' not in data:
        return jsonify({'errors': {'products': {'code': 'missing-fields', 'name': 'La création d\'une commande nécessite un produit'}}}), 422

    if 'products' in data:
        product_data = data['products']
        order_items  = []

        for product_data in product_data:
        
            if 'id' not in product_data or 'quantity' not in product_data:
                return jsonify({'errors': {'products': {'code': 'missing-fields', 'name': 'La création d\'une commande nécessite un produit'}}}), 422

            product_id = product_data['id']
            quantity = product_data['quantity']

            if quantity < 1:
                return jsonify({'errors': {'products': {'code': 'missing-fields', 'name': 'La création d\'une commande nécessite un produit'}}}), 422

            product = Product.get_or_none(id=product_id)

            if product is None or not product.in_stock:
                return jsonify({'errors': {'products': {'code': 'out-of-inventory', 'name': 'Le produit demandé n\'est pas en inventaire'}}}), 422

            total_price += product.price * quantity
            total_weight += product.weight * quantity

            order_item = OrderItem.create(product=product, quantity=quantity) 
            order_items.append(order_item)

        if total_weight < 0.5 :
            shipping_price = 5
        elif total_weight < 2 :
            shipping_price = 10
        else :
            shipping_price = 25
        
        for order_item in order_items:
            order_item.save()

        order = Order.create(total_price=total_price, shipping_price=shipping_price, paid=False, email=None, credit_card=None, shipping_information=None)
        order.order_items.add(order_items)
        
    elif 'product' in data:
        product_data = data['product']
        product_id = product_data['id']
        quantity = product_data['quantity']

        if quantity < 1:
            return jsonify({'errors': {'products': {'code': 'missing-fields', 'name': 'La création d\'une commande nécessite un produit'}}}), 422

        product = Product.get_or_none(id=product_id)

        if product is None or not product.in_stock:
            return jsonify({'errors': {'products': {'code': 'out-of-inventory', 'name': 'Le produit demandé n\'est pas en inventaire'}}}), 422

        total_price += product.price * quantity
        total_weight += product.weight * quantity

        if total_weight < 0.5 :
            shipping_price = 5
        elif total_weight < 2 :
            shipping_price = 10
        else :
            shipping_price = 25

        order_item = OrderItem.create(product=product, quantity=quantity)
        order = Order.create(total_price=total_price, shipping_price=shipping_price, paid=False, email=None, credit_card=None, shipping_information=None)
        order.order_items.add(order_item) 
        
    return redirect(url_for('get_order', order_id=order.id), code=302)


@app.route('/order/<int:order_id>', methods=['GET'])
def get_order(order_id):
    try:
        order = Order.get(id=order_id)
        return jsonify({"order" : order.to_dict()})
    
    except Order.DoesNotExist or order_id is None:
        return jsonify({'errors': {'order': {'code': 'not-found', 'name': 'La commande demandée n\'existe pas'}}}), 404

    
@app.route('/order/<int:order_id>', methods=['PUT'])
def put_order(order_id):
    data = request.get_json()
    order = Order.get_or_none(id=order_id)

    if order is None:
        return jsonify({'errors': {'order': {'code': 'not-found', 'name': 'La commande demandée n\'existe pas'}}}), 404

    if 'order' not in data:
        if 'credit_card' not in data:
            return jsonify({'errors': {'order': {'code': 'missing-fields', 'name': 'Il manque un ou plusieurs champs qui sont obligatoires'}}}), 422

        card_data = data['credit_card']

        if 'number' not in card_data or 'expiration_year' not in card_data or 'expiration_month' not in card_data or 'cvv' not in card_data or 'name' not in card_data :
            return jsonify({'errors': {'order': {'code': 'missing-fields', 'name': 'Il manque un ou plusieurs champs qui sont obligatoires'}}}), 422
        
        if order.email is None or order.shipping_information is None:
            return jsonify({'errors': {'order': {'code': 'missing-fields', 'name': 'Les informations du client sont necessaires avant d\'appliquer une carte de credit'}}}), 422
        
        if order.shipping_information.country is None or order.shipping_information.address is None or order.shipping_information.postal_code is None or order.shipping_information.city is None or order.shipping_information.province is None:
            return jsonify({'errors': {'order': {'code': 'missing-fields', 'name': 'Les informations du client sont necessaires avant d\'appliquer une carte de credit'}}}), 422

        amount_charged = order.total_price + order.shipping_price
        body = {"credit_card": card_data, 'amount_charged': amount_charged}
        req = requests.post('http://dimprojetu.uqac.ca/~jgnault/shops/pay/', json=body)
        req = req.json()
        
        if 'errors' in req:
            return jsonify(req), 422
        
        transaction = req['transaction']
        order.paid = True
        order.transaction = Transaction.create(id=transaction['id'], amount_charged=amount_charged, success = transaction['success'])
        order.credit_card = CreditCard.create(number=card_data['number'], expiration_year=card_data['expiration_year'], expiration_month=card_data['expiration_month'], cvv=card_data['cvv'], name=card_data['name'])    
        order.save()

        return jsonify({"order" : order.to_dict()})
    
    data = data['order']
    
    if 'shipping_information' not in data or 'email' not in data :
        return jsonify({'errors': {'order': {'code': 'missing-fields', 'name': 'Il manque un ou plusieurs champs qui sont obligatoires'}}}), 422
        
    ship_data = data['shipping_information']

    if 'country' not in ship_data or 'address' not in ship_data or 'postal_code' not in ship_data or 'city' not in ship_data or 'province' not in ship_data:
        return jsonify({'errors': {'order': {'code': 'missing-fields', 'name': 'Il manque un ou plusieurs champs qui sont obligatoires'}}}), 422

    order.shipping_information = ShippingInformation.create(country=ship_data['country'], address=ship_data['address'], postal_code=ship_data['postal_code'], city=ship_data['city'], province=ship_data['province'])
    order.email = data['email']
    order.save()

    return jsonify({"order" : order.to_dict()})


if len(sys.argv) > 1 and sys.argv[1] != 'init-db':

    db = PostgresqlDatabase(
        database=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    db.connect()

    response = requests.get('http://dimprojetu.uqac.ca/~jgnault/shops/products/')
    products = response.json()
    products = products['products']

    for product in products:
        if Product.get_or_none(id=product['id']) is None:
            if "\x00" in product["description"]:
                product["description"] = product["description"].replace("\x00", "")
            Product.create(id=product['id'], name=product['name'], type=product['type'], description=product['description'], image=product['image'], price=product['price'], weight=product['weight'], height=product['height'], in_stock=product['in_stock'])

    app.run(debug=True, host='0.0.0.0', port=5000)
