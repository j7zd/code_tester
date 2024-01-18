from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from code_tester import CodeTester, ResultEnum
from datetime import datetime
from threading import Thread
app = Flask(__name__)

auth = '3e2e203d5009dcc4b93c26c5686c24a2461994e153b1da2f083f1a9eb10021bc'

mysql_user = getenv('MYSQL_USER')
mysql_password = getenv('MYSQL_PASSWORD')
mysql_host = getenv('MYSQL_HOST')

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
def test_code():
    code = request.json['code']
    language = request.json['language']
    api_key = request.json['api_key']

    if auth != request.json['auth']:
        return jsonify({'error': 'invalid auth'}), 401
    
    code_tester = None
    try:
        code_tester = CodeTester(code, language)
    except:
        return jsonify({'error': 'invalid language'}), 400
    
    curtime = datetime.now()
    time_str = curtime.strftime('%Y-%m-%d %H:%M')
    code_object = Code(api_key=api_key, language=language, code=code, datetime=time_str, num_tests=code_tester.n_tests())
    db.session.add(code_object)
    db.session.commit()

    t1 = Thread(target=tc, args=(code_tester, code_object.id))
    t1.start()

    return jsonify({'id': code_object.id}), 200

def tc(code_tester: CodeTester, code_id: int):
    with app.app_context():        
        for i in range(code_tester.n_tests()):
            test = code_tester.test(i)
            test = Test(code_id=code_id, test=i, time=test['time'], memory=test['memory'], result=test['result'])
            db.session.add(test)
        db.session.commit()

