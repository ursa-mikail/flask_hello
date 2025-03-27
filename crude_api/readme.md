
A service (flask.get put post delete), and user curl `put, get, post, delete`.

chmod +x run.sh
./run.sh

open_new_window
```

1. Create an item (POST)
curl -X POST -H "Content-Type: application/json" -d '{"value": "example_value"}' http://127.0.0.1:5000/item/example

2. Retrieve an item (GET)
curl -X GET http://127.0.0.1:5000/item/example

3. Update an item (PUT)
curl -X PUT -H "Content-Type: application/json" -d '{"value": "new_value"}' http://127.0.0.1:5000/item/example

4. Delete an item (DELETE)
curl -X DELETE http://127.0.0.1:5000/item/example
```

[ctrl-z]
