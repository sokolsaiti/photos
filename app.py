import os
import sqlite3

from flask import Flask, g, render_template, send_from_directory, redirect, abort

from conf.settings import UPLOAD_DIR, PAGE_SIZE, BASE_URL, DATABASE, PHOTO_DIR

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
def index(page=1):
    photos = get_photos(page_size=PAGE_SIZE, page=page - 1)
    previous_page = False
    if page > 1:
        previous_page = True
    if len(photos) > 0:
        return render_template('index.html', base_url=BASE_URL, photo_list=photos, current_page=page,
                               has_previous_page=previous_page)
    else:
        return redirect('/')


@app.route('/p/<int:photo_id>')
def single_photo(photo_id=-1):
    photo = get_photo(photo_id)
    if len(photo) > 0:
        return render_template('single.html', base_url=BASE_URL, photo_list=photo)
    else:
        abort(404)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


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


def get_photo(id):
    with app.app_context():
        cursor = get_db().execute("SELECT file_id,datetime_added FROM photos WHERE file_id = ?", (id,))
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
