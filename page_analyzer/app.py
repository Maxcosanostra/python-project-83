import os
import requests
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from datetime import datetime
from page_analyzer.db import connect_db, commit, close, insert_url, \
    get_url, get_urls, insert_url_check, get_url_checks
from page_analyzer.html_parser import parse_html
from page_analyzer.url_utils import normalize_url, validate_url

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


@app.template_filter('datetime')
def datetime_filter(value):
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    return value


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/list_urls', methods=['GET', 'POST'])
def list_urls():
    conn = connect_db(app)
    if request.method == 'POST':
        url = request.form['url']
        if not validate_url(url):
            flash('Некорректный URL!', 'danger')
            return redirect(url_for('index'))

        url = normalize_url(url)
        try:
            url_id = insert_url(conn, url)
            commit(conn)
            flash('URL успешно добавлен!', 'success')
        except psycopg2.IntegrityError:
            conn.rollback()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM urls WHERE name = %s;", (url,))
            url_id = cursor.fetchone()[0]
            cursor.close()
            flash('Страница уже существует', 'info')
        finally:
            close(conn)
        return redirect(url_for('view_url', id=url_id))

    urls = get_urls(conn)
    close(conn)
    return render_template('list_urls.html', urls=urls)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url(id):
    conn = connect_db(app)
    url = get_url(conn, id)
    if url is None:
        flash('URL не найден!', 'danger')
        close(conn)
        return redirect(url_for('list_urls'))

    try:
        response = requests.get(url.name)
        response.raise_for_status()
        status_code = response.status_code
        parsed_content = parse_html(response.text)
    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        close(conn)
        return redirect(url_for('view_url', id=id))

    insert_url_check(
        conn, id, status_code, parsed_content['h1'],
        parsed_content['title'], parsed_content['description']
    )
    commit(conn)
    close(conn)
    flash('Проверка успешно запущена!', 'success')
    return redirect(url_for('view_url', id=id))


@app.route('/view_url/<int:id>')
def view_url(id):
    conn = connect_db(app)
    url = get_url(conn, id)
    checks = get_url_checks(conn, id)
    close(conn)
    if url is None:
        flash('URL не найден!', 'danger')
        return redirect(url_for('list_urls'))
    return render_template('view_url.html', url=url, checks=checks)


@app.errorhandler(500)
def internal_error(error):
    return "Internal Server Error", 500


@app.errorhandler(Exception)
def unhandled_exception(e):
    return "Internal Server Error", 500


if __name__ == '__main__':
    app.run()
