from flask import Flask
from .navigation import Navigation

app = Flask(__name__)

nus_navigation = Navigation()

@app.route('/api/locations', methods=['GET'])
def get_all_locations():
    return nus_navigation.get_all_locations()
