from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from enum import Enum
import requests

user = 'root'#getenv('MYSQL_USER')
password = 'root'#getenv('MYSQL_PASSWORD')
host = '172.18.0.2'#getenv('MYSQL_HOST')
code_tester_host = getenv('CODE_TESTER_HOST')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{user}:{password}@{host}/code'
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

with app.app_context():
    db.drop_all()
    db.create_all()

    # FOR TESTING
    code = Code(api_key='test', language='C++', code='from os import getenv\nimport sqlalchemy as db\n\ndef test_code(code: str):\n    host = getenv(\'MYSQL_HOST\')\n    user = getenv(\'MYSQL_USER\')\n    password = getenv(\'MYSQL_PASSWORD\')\n    database = getenv(\'MYSQL_DATABASE\')\n\n    engine = db.create_engine(f\'mysql+pymysql://{user}:{password}@{host}/{database}\')\n    connection = engine.connect()\n    metadata = db.MetaData()\n', datetime='2020-01-01 00:00', num_tests=3)
    db.session.add(code)
    test = Test(code_id=1, test=1, time=0.1, memory=100, result=ResultEnum.OK)
    db.session.add(test)
    test = Test(code_id=1, test=2, time=0.2, memory=200, result=ResultEnum.WA)
    db.session.add(test)
    test = Test(code_id=1, test=3, time=0.3, memory=300, result=ResultEnum.TL)
    db.session.add(test)

    db.session.commit()
    #############

@app.route('/code', methods=['POST'])
def post_code():
    pass

@app.route('/result', methods=['GET'])
def get_result():
    api_key = request.args.get('api_key')
    id = request.args.get('id')
    
    tests = Test.query.filter_by(code_id=id).all()
    code = Code.query.filter_by(id=id).first()

    return jsonify({'datetime': code.datetime, 'num_tests': code.num_tests, 'tests': [{'test': test.test, 'time': test.time, 'memory': test.memory, 'result': test.result.name} for test in tests]})
