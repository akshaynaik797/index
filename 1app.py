from flask import Flask
from flask_cors import CORS


app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['referrer_url'] = None


@app.route("/")
def index():
    return 'hello from logs_api'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9989)
