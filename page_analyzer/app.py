import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from page_analyzer import db
from page_analyzer.html_parser import parse_html
from page_analyzer.utils import normalize_url, validate_url


load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


@app.get('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def list_urls():
    conn = db.connect_db(app)
    urls = db.get_urls(conn)
    db.close(conn)
    return render_template('list_urls.html', urls=urls)


@app.post('/urls')
def add_url():
    url = request.form['url']
    error_msg = validate_url(url)
    if error_msg:
        flash(error_msg, 'danger')
        return render_template('index.html', url=url), 422

    conn = db.connect_db(app)
    normalized_url = normalize_url(url)
    existed_url = db.get_url_by_name(conn, normalized_url)

    if existed_url:
        flash('Страница уже существует', 'info')
        url_id = existed_url.id
    else:
        url_id = db.insert_url(conn, normalized_url)
        db.commit(conn)
        flash('Страница успешно добавлена', 'success')

    db.close(conn)
    return redirect(url_for('url_details', id=url_id))


@app.post('/urls/<int:id>/checks')
def check_url(id):
    return validate_url_check(id)


@app.get('/urls/<int:id>')
def url_details(id):
    conn = db.connect_db(app)
    url = db.get_url(conn, id)
    checks = db.get_url_checks(conn, id)
    db.close(conn)
    return render_template('view_url.html', url=url, checks=checks)


def validate_url_check(url_id):
    conn = db.connect_db(app)
    url = db.get_url(conn, url_id)
    try:
        response = requests.get(url.name)
        response.raise_for_status()
    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('url_details', id=url_id))

    page_data = parse_page_content(response)
    db.insert_url_check(conn, url_id, page_data)
    db.commit(conn)
    db.close(conn)
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('url_details', id=url_id))

def parse_page_content(response):
    parsed_content = parse_html(response.text)
    return {
        'status_code': response.status_code,
        'h1': parsed_content['h1'],
        'title': parsed_content['title'],
        'description': parsed_content['description'],
    }


@app.errorhandler(500)
def internal_error(error):
    return "Internal Server Error", 500


@app.errorhandler(Exception)
def unhandled_exception(e):
    return "Internal Server Error", 500


if __name__ == '__main__':
    app.run()
