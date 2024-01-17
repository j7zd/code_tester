from Flask import Flask, jsonify
import code_tester
app = Flask(__name__)

@app.route('/code', methods=['POST'])
def post_code():
    

@app.route('/result', methods=['GET'])
def get_result():
    pass