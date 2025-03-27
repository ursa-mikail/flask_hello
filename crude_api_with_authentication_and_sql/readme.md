

✅ Authentication → Uses an API Key (X-API-KEY header).
✅ Database Storage → Uses SQLite instead of an in-memory dictionary.
✅ Logging → Logs requests for monitoring.
✅ Security → Unauthorized access returns a 403 Forbidden error.


chmod +x run.sh
./run.sh

open_new_window
```

1. Create an item (POST)
curl -X POST -H "X-API-KEY: my_secret_key" -H "Content-Type: application/json" \
     -d '{"value": "example_value"}' http://127.0.0.1:5000/item/example

2. Retrieve an item (GET)
curl -X GET -H "X-API-KEY: my_secret_key" http://127.0.0.1:5000/item/example

3. Update an item (PUT)
curl -X PUT -H "X-API-KEY: my_secret_key" -H "Content-Type: application/json" \
     -d '{"value": "new_value"}' http://127.0.0.1:5000/item/example

4. Delete an item (DELETE)
curl -X DELETE -H "X-API-KEY: my_secret_key" http://127.0.0.1:5000/item/example
```

[ctrl-z]

## Version of the Flask service with the following additional features:
To change this version (not done in this version):
✅ JWT Authentication → Protects all item routes.
✅ Rate Limiting → Limits the number of requests per IP address.
✅ Redis Caching → Improves performance by caching responses for a short time.
✅ Flask SQLAlchemy → Stores item data persistently in SQLite.


### Setup Instructions
1. Install additional dependencies:

pip install flask flask_sqlalchemy pyjwt flask_limiter redis

2. Set up Redis on your local machine or use a Redis service:

![Install Redis locally](https://redis.io/docs/getting-started/)

3. Run:
python app.py

Flask Service (app.py)
```
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import jwt
import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
import os

# Initialize Flask app, database, and Redis client
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")
db = SQLAlchemy(app)

# Initialize rate limiter
limiter = Limiter(app, key_func=get_remote_address)

# Initialize Redis cache
cache = redis.StrictRedis(host='localhost', port=6379, db=0)

# Define Model
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.String(500), nullable=False)

# Create Database
with app.app_context():
    db.create_all()

# JWT Token generation
def generate_token(username):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    token = jwt.encode({"sub": username, "exp": expiration}, app.secret_key, algorithm="HS256")
    return token

# JWT Token verification
def verify_token(token):
    try:
        payload = jwt.decode(token, app.secret_key, algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Authentication middleware
def authenticate():
    token = request.headers.get("Authorization")
    if token:
        username = verify_token(token)
        if username:
            return username
    return None

# Rate limiting - 5 requests per minute per IP
@app.route('/item/<string:key>', methods=['GET'])
@limiter.limit("5 per minute")
def get_item(key):
    """Retrieve an item by key."""
    username = authenticate()
    if not username:
        return jsonify({"error": "Unauthorized"}), 403
    
    cached_value = cache.get(key)
    if cached_value:
        return jsonify({key: cached_value.decode('utf-8')})
    
    item = Item.query.filter_by(key=key).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    cache.setex(key, 60, item.value)  # Cache for 60 seconds
    return jsonify({item.key: item.value})

@app.route('/item/<string:key>', methods=['POST'])
@limiter.limit("5 per minute")
def post_item(key):
    """Create a new item (fails if the key already exists)."""
    username = authenticate()
    if not username:
        return jsonify({"error": "Unauthorized"}), 403
    
    if Item.query.filter_by(key=key).first():
        return jsonify({'error': 'Item already exists'}), 400
    
    value = request.json.get('value')
    new_item = Item(key=key, value=value)
    db.session.add(new_item)
    db.session.commit()
    
    cache.setex(key, 60, value)  # Cache for 60 seconds
    return jsonify({key: value}), 201

@app.route('/item/<string:key>', methods=['PUT'])
@limiter.limit("5 per minute")
def put_item(key):
    """Update an existing item (or create if not exists)."""
    username = authenticate()
    if not username:
        return jsonify({"error": "Unauthorized"}), 403
    
    value = request.json.get('value')
    item = Item.query.filter_by(key=key).first()

    if item:
        item.value = value
    else:
        item = Item(key=key, value=value)
        db.session.add(item)
    
    db.session.commit()
    
    cache.setex(key, 60, value)  # Cache for 60 seconds
    return jsonify({key: value})

@app.route('/item/<string:key>', methods=['DELETE'])
@limiter.limit("5 per minute")
def delete_item(key):
    """Delete an item by key."""
    username = authenticate()
    if not username:
        return jsonify({"error": "Unauthorized"}), 403
    
    item = Item.query.filter_by(key=key).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        cache.delete(key)  # Remove from cache
        return jsonify({'message': 'Item deleted'}), 200
    
    return jsonify({'error': 'Item not found'}), 404

@app.route('/login', methods=['POST'])
def login():
    """Generate JWT token for valid users."""
    username = request.json.get('username')
    password = request.json.get('password')
    # Here you would verify the user credentials (this is just a placeholder)
    if username == "admin" and password == "password":
        token = generate_token(username)
        return jsonify({"token": token}), 200
    return jsonify({"error": "Invalid credentials"}), 401

if __name__ == '__main__':
    app.run(debug=True)
```

### Key Features
JWT Authentication

The /login endpoint provides a JWT token when valid credentials are given.

The token is used in the Authorization header of each request to authenticate the user.

Rate Limiting

A rate limit of 5 requests per minute per IP address is applied to all item routes.

Redis Caching

When retrieving an item, the result is cached in Redis for 60 seconds to improve performance.

Flask SQLAlchemy Database

Items are stored in an SQLite database and can be retrieved, created, updated, or deleted.

cURL Examples
1. Login to Get JWT Token
curl -X POST -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "password"}' \
     http://127.0.0.1:5000/login

The response will contain the JWT token:

{
  "token": "your-jwt-token"
}

2. Create an item (POST)
curl -X POST -H "Authorization: Bearer your-jwt-token" -H "Content-Type: application/json" \
     -d '{"value": "example_value"}' http://127.0.0.1:5000/item/example

3. Retrieve an item (GET)
curl -X GET -H "Authorization: Bearer your-jwt-token" http://127.0.0.1:5000/item/example

4. Update an item (PUT)
curl -X PUT -H "Authorization: Bearer your-jwt-token" -H "Content-Type: application/json" \
     -d '{"value": "new_value"}' http://127.0.0.1:5000/item/example

5. Delete an item (DELETE)
curl -X DELETE -H "Authorization: Bearer your-jwt-token" http://127.0.0.1:5000/item/example
