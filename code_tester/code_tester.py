from os import getenv
import sqlalchemy as db

def test_code(code: str):
    host = getenv('MYSQL_HOST')
    user = getenv('MYSQL_USER')
    password = getenv('MYSQL_PASSWORD')
    database = getenv('MYSQL_DATABASE')

    engine = db.create_engine(f'mysql+pymysql://{user}:{password}@{host}/{database}')
    connection = engine.connect()
    metadata = db.MetaData()
    
