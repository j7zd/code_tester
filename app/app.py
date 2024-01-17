from flask import Flask, jsonify, request
from os import getenv
app = Flask(__name__)



@app.route('/code', methods=['POST'])
def post_code():
    code = request.json['code']
    print(code)

    return jsonify({'code': code})
