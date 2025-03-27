from flask import Flask, render_template
import webbrowser
import threading

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    threading.Timer(1.25, open_browser).start()  # Auto-open browser
    app.run(debug=True)

