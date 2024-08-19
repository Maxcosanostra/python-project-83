import os
import requests
from flask import Flask, render_template, request, redirect, \
    url_for, flash, abort
from dotenv import load_dotenv
from page_analyzer import db
from page_analyzer.html_parser import parse_html
from page_analyzer.utils import normalize_url, validate_url


load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    return render_template('index.html')


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
    return redirect(url_for('show_url_page', url_id=url_id))


@app.route('/urls/<int:url_id>')
def show_url_page(url_id):
    conn = db.connect_db(app)
    url = db.get_url(conn, url_id)
    if not url:
        abort(404)

    url_checks = db.get_checks_by_url_id(conn, url_id)
    db.close(conn)
    return render_template('urls/view_url.html', url=url, checks=url_checks)


@app.get('/urls')
def show_urls_page():
    conn = db.connect_db(app)
    urls_data = db.get_urls_with_last_check_date_and_status_code(conn)
    db.close(conn)
    return render_template('urls/list_urls.html', urls=urls_data)


@app.post('/urls/<int:url_id>/checks')
def process_url_check(url_id):
    conn = db.connect_db(app)
    url = db.get_url(conn, url_id)
    try:
        response = requests.get(url.name)
        response.raise_for_status()
    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('show_url_page', url_id=url_id))

    page_data = parse_html(response)
    db.insert_url_check(conn, url_id, page_data)
    db.commit(conn)
    db.close(conn)
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('show_url_page', url_id=url_id))


@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404
