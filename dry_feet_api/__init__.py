from flask import Flask, jsonify, request
from flask_cors import CORS
from .navigation import Navigation

app = Flask(__name__)
CORS(app)

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
    path_result = nus_navigation.find_path(src_location, dst_location, sheltered, accessible)
    if path_result is None:
        route = None
        points = None
    else:
        route, points = path_result
    response = {"possible": route is not None, "route": route, "points": points}
    return jsonify(response)
