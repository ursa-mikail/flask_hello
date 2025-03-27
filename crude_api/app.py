from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory data storage
data_store = {}

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
    item = data_store.get(key)
    if item is None:
        return jsonify({'error': 'Item not found'}), 404
    return jsonify({key: item})

@app.route('/item/<string:key>', methods=['POST'])
def post_item(key):
    """Create a new item (fails if the key already exists)."""
    if key in data_store:
        return jsonify({'error': 'Item already exists'}), 400
    data_store[key] = request.json.get('value')
    return jsonify({key: data_store[key]}), 201

@app.route('/item/<string:key>', methods=['PUT'])
def put_item(key):
    """Update an existing item (or create if not exists)."""
    data_store[key] = request.json.get('value')
    return jsonify({key: data_store[key]})

@app.route('/item/<string:key>', methods=['DELETE'])
def delete_item(key):
    """Delete an item by key."""
    if key in data_store:
        del data_store[key]
        return jsonify({'message': 'Item deleted'}), 200
    return jsonify({'error': 'Item not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)

