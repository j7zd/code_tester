import requests
from time import sleep

r = requests.get('http://localhost:5000/languages')
print(r.json())
assert r.status_code == 200
lang = r.json()['languages'][0]

r = requests.get('http://localhost:5000/problems')
print(r.json())
assert r.status_code == 200
problem = r.json()['problems'][0]

r = requests.post('http://localhost:5000/code', json={'code': 'int main() {return 0;}', 'language': lang, 'problem': problem, 'api_key': 'f2ca1bb6c7e907d06dafe4687e579fce76b37e4e93b7605022da52e6ccc26fd2'})
print(r.json())
assert r.status_code == 200
id = r.json()['id']

while True:
    r = requests.get(f'http://localhost:5000/result/{id}', params={'api_key': 'f2ca1bb6c7e907d06dafe4687e579fce76b37e4e93b7605022da52e6ccc26fd2'})
    assert r.status_code == 200
    print(r.json())
    if len(r.json()['tests']) != 0:
        break
    sleep(0.1)

r = requests.post('http://localhost:5000/code', json={'code': '#include<iostream>\nusing namespace std; int main() {int a, b, c; cin>>a>>b>>c; cout<<c<<" "<<b<<" "<<a<<endl; return 0;}', 'language': lang, 'problem': problem, 'api_key': 'f2ca1bb6c7e907d06dafe4687e579fce76b37e4e93b7605022da52e6ccc26fd2'})
print(r.json())
assert r.status_code == 200
id = r.json()['id']

while True:
    r = requests.get(f'http://localhost:5000/result/{id}', params={'api_key': 'f2ca1bb6c7e907d06dafe4687e579fce76b37e4e93b7605022da52e6ccc26fd2'})
    assert r.status_code == 200
    print(r.json())
    if len(r.json()['tests']) != 0:
        break
    sleep(0.1)

r = requests.get(f'http://localhost:5000/results', params={'api_key': 'f2ca1bb6c7e907d06dafe4687e579fce76b37e4e93b7605022da52e6ccc26fd2'})
print(r.json())
assert r.status_code == 200

r = requests.get(f'http://localhost:5000/results', params={'api_key': 'wrong api key'})
print(r.json())
assert r.status_code == 403
