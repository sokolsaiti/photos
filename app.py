import sqlite3

from flask import Flask, g

DATABASE = 'database.db'

app = Flask(__name__)


@app.route('/<int:page>')
def hello_world(page=1):
    if page is None:
        return 'Hello, world!'
    else:
        return str(page)


@app.route('/test')
def test_hello():
    return 'Hello Test.'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('db/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


if __name__ == '__main__':
    app.run()
