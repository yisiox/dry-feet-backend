from flask import Flask, jsonify, request
from .navigation import Navigation

app = Flask(__name__)

nus_navigation = Navigation()

@app.route('/api/locations', methods=['GET'])
def get_all_locations():
    return jsonify(nus_navigation.get_all_locations())

@app.route('/api/find_path', methods=['GET'])
def find_path():
    src_location = request.args.get('from')
    dst_location = request.args.get('to')
    sheltered = 'sheltered' in request.args
    accessible = 'accessible' in request.args
    route = nus_navigation.find_path(src_location, dst_location, sheltered, accessible)
    if route is None:
        return jsonify({"possible": False, "route": route})
    return jsonify({"possible": True, "route": route})
