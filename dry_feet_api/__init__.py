from flask import Flask

app = Flask(__name__)

@app.route('/api', methods=['GET'])
def home():
    return "Hello world!"
