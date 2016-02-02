import sqlite3
from flask import Flask
app = Flask(__name__)


DATABASE = 'transfers.db'

def get_db():
    db = getattr(Flask, '_database', None)
    if db is None:
        db = Flask._database = connect_to_database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(Flask, '_database', None)
    if db is not None:
        db.close()


get_db()

if __name__ == '__main__':
    app.run()