import os
import sqlite3

from flask import Flask, g, render_template, send_from_directory

DATABASE = 'photo_repository.db'
# UPLOAD_DIR = '/home/' + getpass.getuser() + '/uploads/photos'
UPLOAD_DIR = 'uploads/photos'
PHOTO_DIR = 'static/photos'
PAGE_SIZE = 5

app = Flask(__name__)

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


@app.route('/static/img/<path:path>')
def send_photo(path):
    return send_from_directory('static/img', path)


@app.route('/static/css/<path:path>')
def send_css(path):
    return send_from_directory('static/css', path)


@app.route('/')
@app.route('/<int:page>')
def hello_world(page=1):
    return render_template('index.html', photo_list=get_photos(page_size=PAGE_SIZE, page=page - 1))


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


def collect_uploads():
    with app.app_context():
        uploaded_files = os.listdir(UPLOAD_DIR)
        for file in uploaded_files:
            file_id = insert_photo(file)
            os.rename(UPLOAD_DIR + '/' + file, PHOTO_DIR + '/' + str(file_id) + '.JPG')


def get_photos(page_size, page):
    with app.app_context():
        cursor = get_db().execute(
            "SELECT file_id,datetime_added FROM photos  WHERE oid NOT IN ( SELECT oid FROM photos ORDER BY file_id desc LIMIT ? * ? ) ORDER BY file_id desc LIMIT ?",
            (page_size, page, page_size,))
        result = cursor.fetchall()
        cursor.close()
        return result


def uncollect_uploads():
    uploaded_files = os.listdir(PHOTO_DIR)
    for file in uploaded_files:
        os.rename(PHOTO_DIR + '/' + file, UPLOAD_DIR + '/' + file)


def insert_photo(original_file_name):
    cursor = get_db().execute("insert into photos (original_file_name, datetime_added) values(?, datetime('now'))",
                              (original_file_name,))
    get_db().commit()
    last_row = cursor.lastrowid
    cursor.close()
    return last_row


def query_db(query, args=(), one=False):
    cursor = get_db().execute(query, args)
    rows = cursor.fetchall()
    cursor.close()
    return (rows[0] if rows else None) if one else rows


if __name__ == '__main__':
    app.run()
