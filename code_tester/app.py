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

# FOR TESTING
# mysql_host = '172.18.0.2:3306'
# mysql_user = 'root'
# mysql_password = 'root'

# app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/code'
#############

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
    #db.drop_all()
    db.create_all()

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
        for i in range(1, code_tester.n_tests() + 1):
            test = code_tester.test(i)
            test = Test(code_id=code_id, test=i, time=test['time'], memory=test['memory'], result=test['result'])
            db.session.add(test)
        db.session.commit()
# UNIT TESTS
# if __name__ == '__main__':
#     t1 = Thread(target=app.run)
#     t1.start()
#     import requests
    
#     r = requests.post('http://localhost:5000/code', json={'code': 'int main() {return 0;}', 'language': '1_c++', 'api_key': 'test', 'auth': 'wrong auth key'})
#     print(r.json())
#     assert r.status_code == 401

#     r = requests.post('http://localhost:5000/code', json={'code': 'int main() {return 0;}', 'language': '1_c--', 'api_key': 'test', 'auth': auth})
#     print(r.json())
#     assert r.status_code == 400

#     r = requests.post('http://localhost:5000/code', json={'code': 'int main() {return 0;}', 'language': '1_c++', 'api_key': 'test', 'auth': auth})
#     print(r.json())
#     assert r.status_code == 200
#     with app.app_context():
#         cd = Code.query.filter_by(id=r.json()['id']).first()
#         assert cd is not None
#         assert cd.api_key == 'test'
#         assert cd.language == '1_c++'
#         assert cd.code == 'int main() {return 0;}'
#         Code.query.filter_by(id=r.json()['id']).delete()
#         db.session.commit()

#     t1.join()
############
