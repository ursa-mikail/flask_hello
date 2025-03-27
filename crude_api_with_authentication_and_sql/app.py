from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import logging
import os

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Logging Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Authentication API Key
API_KEY = os.getenv("API_KEY", "my_secret_key")

# Define Model
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.String(500), nullable=False)

# Create Database
with app.app_context():
    db.create_all()

# Authentication Middleware
def authenticate():
    api_key = request.headers.get("X-API-KEY")
    if api_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 403

@app.route('/')
def home():
    return """
    <h1>Welcome to the Flask API</h1>
    <p>Use the endpoints to interact with the service.</p>
    <ul>
        <li><strong>GET</strong> /item/&lt;key&gt; - Retrieve an item</li>
        <li><strong>POST</strong> /item/&lt;key&gt; - Create an item</li>
        <li><strong>PUT</strong> /item/&lt;key&gt; - Update an item</li>
        <li><strong>DELETE</strong> /item/&lt;key&gt; - Delete an item</li>
    </ul>
    """
    
@app.route('/item/<string:key>', methods=['GET'])
def get_item(key):
    """Retrieve an item by key."""
    auth = authenticate()
    if auth: return auth
    
    item = Item.query.filter_by(key=key).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    return jsonify({item.key: item.value})

@app.route('/item/<string:key>', methods=['POST'])
def post_item(key):
    """Create a new item (fails if the key already exists)."""
    auth = authenticate()
    if auth: return auth
    
    if Item.query.filter_by(key=key).first():
        return jsonify({'error': 'Item already exists'}), 400
    
    value = request.json.get('value')
    new_item = Item(key=key, value=value)
    db.session.add(new_item)
    db.session.commit()
    
    return jsonify({key: value}), 201

@app.route('/item/<string:key>', methods=['PUT'])
def put_item(key):
    """Update an existing item (or create if not exists)."""
    auth = authenticate()
    if auth: return auth
    
    value = request.json.get('value')
    item = Item.query.filter_by(key=key).first()

    if item:
        item.value = value
    else:
        item = Item(key=key, value=value)
        db.session.add(item)
    
    db.session.commit()
    return jsonify({key: value})

@app.route('/item/<string:key>', methods=['DELETE'])
def delete_item(key):
    """Delete an item by key."""
    auth = authenticate()
    if auth: return auth
    
    item = Item.query.filter_by(key=key).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Item deleted'}), 200
    
    return jsonify({'error': 'Item not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)



