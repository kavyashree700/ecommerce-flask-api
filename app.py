from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import(
    JWTManager,
    create_access_token,
    jwt_required
)
from config import Config
import bcrypt

app = Flask(__name__)
app.config.from_object(Config)

app.config['JWT_SECRET_KEY'] = 'mysecretkey'

db = SQLAlchemy(app)

jwt = JWTManager(app)

# ---------------- USER TABLE ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

# ---------------- PRODUCT TABLE ----------------
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    stock = db.Column(db.Integer)

# ---------------- ORDER TABLE ----------------
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100))
    product_name = db.Column(db.String(100))
    quantity = db.Column(db.Integer)

# ---------------- CART TABLE ----------------
class Cart(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer)

    product_id = db.Column(db.Integer)

    quantity = db.Column(db.Integer)

# ---------------- HOME ROUTE ----------------
@app.route('/')
def home():
    return "E-Commerce API Running Successfully!"

# ---------------- REGISTER API ----------------
@app.route('/register', methods=['POST'])
def register():

    data = request.get_json()

    name = data['name']
    email = data['email']
    password = data['password']

    # Convert password to encrypted form
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Create user object
    new_user = User(
        name=name,
        email=email,
        password=hashed_password
    )

    # Save to database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully"
    })

# ---------------- LOGIN API ----------------
@app.route('/login', methods=['POST'])
def login():

    data = request.get_json()

    email = data['email']
    password = data['password']

    # Find user in database
    user = User.query.filter_by(email=email).first()

    if user:

        # Check password
        if bcrypt.checkpw(password.encode('utf-8'), user.password):

            access_token = create_access_token(identity=email)

            return jsonify({
                 "message": "Login successful",
                 "token": access_token
            })

    return jsonify({
        "message": "Invalid email or password"
    })

# ---------------- ADD TO CART API ----------------
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():

    data = request.get_json()

    user_id = data['user_id']
    product_id = data['product_id']
    quantity = data['quantity']

    cart_item = Cart(
        user_id=user_id,
        product_id=product_id,
        quantity=quantity
    )

    db.session.add(cart_item)
    db.session.commit()

    return jsonify({
        "message": "Product added to cart"
    })

# ---------------- VIEW CART API ----------------
@app.route('/cart', methods=['GET'])
def view_cart():

    cart_items = Cart.query.all()

    output = []

    for item in cart_items:

        product = Product.query.get(item.product_id)

        cart_data = {
            "cart_id": item.id,
            "user_id": item.user_id,
            "product_name": product.name,
            "quantity": item.quantity,
            "price": product.price
        }

        output.append(cart_data)

    return jsonify(output)

# ---------------- REMOVE FROM CART API ----------------
@app.route('/remove_from_cart/<int:id>', methods=['DELETE'])
def remove_from_cart(id):

    cart_item = Cart.query.get(id)

    if not cart_item:

        return jsonify({
            "message": "Cart item not found"
        })

    db.session.delete(cart_item)
    db.session.commit()

    return jsonify({
        "message": "Item removed from cart"
    })

# ---------------- PLACE ORDER API ----------------
@app.route('/place_order', methods=['POST'])
def place_order():

    data = request.get_json()

    email = data['email']
    product_name = data['product_name']
    quantity = data['quantity']

    # Find product
    product = Product.query.filter_by(name=product_name).first()

    if not product:
        return jsonify({
            "message": "Product not found"
        })

    # Check stock
    if product.stock < quantity:
        return jsonify({
            "message": "Insufficient stock"
        })

    # Reduce stock
    product.stock -= quantity

    # Create order
    new_order = Order(
        user_email=email,
        product_name=product_name,
        quantity=quantity
    )

    db.session.add(new_order)
    db.session.commit()

    return jsonify({
        "message": "Order placed successfully"
    })


# ---------------- VIEW ORDERS API ----------------
@app.route('/orders', methods=['GET'])
def get_orders():

    orders = Order.query.all()

    output = []

    for order in orders:

        order_data = {
            "id": order.id,
            "user_email": order.user_email,
            "product_name": order.product_name,
            "quantity": order.quantity
        }

        output.append(order_data)

    return jsonify(output)

# ---------------- RECOMMEND PRODUCTS API ----------------
@app.route('/recommend/<int:max_price>', methods=['GET'])
def recommend_products(max_price):

    products = Product.query.filter(Product.price <= max_price).all()

    output = []

    for product in products:

        product_data = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "stock": product.stock
        }

        output.append(product_data)

    return jsonify(output)


# ---------------- CREATE DATABASE ----------------
with app.app_context():
    db.create_all()

# ---------------- ADD PRODUCT API ----------------
@app.route('/add_product', methods=['POST'])
def add_product():

    data = request.get_json()

    name = data['name']
    price = data['price']
    stock = data['stock']

    new_product = Product(
        name=name,
        price=price,
        stock=stock
    )

    db.session.add(new_product)
    db.session.commit()

    return jsonify({
        "message": "Product added successfully"
    })


# ---------------- VIEW PRODUCTS API ----------------
@app.route('/products', methods=['GET'])
@jwt_required()
def get_products():

    products = Product.query.all()

    output = []

    for product in products:

        product_data = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "stock": product.stock
        }

        output.append(product_data)

    return jsonify(output)

# ---------------- RUN APP ----------------
if __name__ == '__main__':
    app.run(debug=True)