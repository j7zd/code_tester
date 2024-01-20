from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from enum import Enum
import requests
from math import ceil
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
import json

auth = '3e2e203d5009dcc4b93c26c5686c24a2461994e153b1da2f083f1a9eb10021bc'

mysql_user = getenv('MYSQL_USER')
mysql_password = getenv('MYSQL_PASSWORD')
mysql_host = getenv('MYSQL_HOST')
code_tester_host = getenv('CODE_TESTER_HOST')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/code'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Code(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(256), nullable=False)
    language = db.Column(db.String(256), nullable=False) #will hold what test to use for this code
    code = db.Column(db.Text, nullable=False)
    datetime = db.Column(db.Date, nullable=False)
    num_tests = db.Column(db.Integer, nullable=False)
class ResultEnum(Enum):
    OK = 1
    WA = 2
    TL = 3
    ML = 4
    RE = 5
    CE = 6 
class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code_id = db.Column(db.Integer, db.ForeignKey('code.id'), nullable=False)
    test = db.Column(db.Integer, nullable=False)
    time = db.Column(db.Float, nullable=False)
    memory = db.Column(db.Integer, nullable=False)
    result = db.Column(db.Enum(ResultEnum), nullable=False)
class Keys(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(256), nullable=False)
    user_level = db.Column(db.Integer, nullable=False)

with app.app_context():
    #b.drop_all()
    db.create_all()

@app.route('/languages', methods=['GET'])
def get_languages():
    return jsonify({'languages': ['c++']})

@app.route('/problems', methods=['GET'])
def get_problems():
    return jsonify({'problems': ['1']})

@app.route('/code', methods=['POST'])
def post_code():
    code = request.json['code']
    language = request.json['problem'] + '_' + request.json['language']
    api_key = request.json['api_key']

    #check if api key is valid
    key = Keys.query.filter_by(api_key=api_key).first()
    if key is None:
        return jsonify({'error': 'invalid api key'}), 403
    
    #send code to code tester
    res = requests.post('http://'+code_tester_host+':5000/code', json={'code': code, 'language': language, 'api_key': api_key, 'auth': auth})
    if res.status_code != 200:
        return jsonify({'error': 'code tester error'}), 500
    return jsonify({'id': res.json()['id']})

@app.route('/result/<id>', methods=['GET'])
def get_result(id):
    api_key = request.args.get('api_key')
    
    code = Code.query.filter_by(id=id).first()

    if code is None:
        return jsonify({'error': 'invalid id'}), 404
    if code.api_key != api_key:
        return jsonify({'error': 'invalid api key'}), 403

    tests = Test.query.filter_by(code_id=id).all()

    return jsonify({'code': code.code, 'datetime': code.datetime, 'num_tests': code.num_tests, 'tests': [{'test': test.test, 'time': test.time, 'memory': test.memory, 'result': test.result.name} for test in tests]})

@app.route('/results', methods=['GET'])
def get_results():
    api_key = request.args.get('api_key')
    page = request.args.get('page')
    per_page = request.args.get('per_page')
    
    key = Keys.query.filter_by(api_key=api_key).first()
    if key is None:
        return jsonify({'error': 'invalid api key'}), 403

    code_query = Code.query.filter_by(api_key=api_key)

    if per_page is None:
        code = code_query.all()
        return jsonify({'ids': [code.id for code in code]})
    if page is None:
        c = code_query.count()
        return jsonify({'pages': ceil(c/int(per_page))})

    code = code_query.paginate(page=int(page), per_page=int(per_page))

    return jsonify({'ids': [code.id for code in code.items]})




@app.route('/swagger', methods=['GET'])
def get_swagger():
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "Code Tester API"
    with open('swagger_paths.json', 'r') as f:
        swag['paths'] = json.load(f)
    return jsonify(swag)

SWAGGER_URL = '/swagger-ui'
API_URL = '/swagger'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Code tester API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)