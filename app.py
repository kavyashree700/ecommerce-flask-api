from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Config
import bcrypt

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

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

            return jsonify({
                "message": "Login successful"
            })

    return jsonify({
        "message": "Invalid email or password"
    })

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