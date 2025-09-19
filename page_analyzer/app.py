from flask import Flask


app = Flask(__name__)


@app.route("/")
def test_handler():
    return "test handler", 200
