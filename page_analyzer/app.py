import os
import requests
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from page_analyzer.db import open_db_connection, close_db_connection, get_url_by_id, fetch_and_parse_url, insert_url_check, check_url_exists, insert_new_url, get_all_urls, get_url_details
import validators
from datetime import datetime
from page_analyzer.utils import format_date, normalize_url


load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


app.jinja_env.filters['datetime'] = format_date


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/list_urls', methods=['GET', 'POST'])
def list_urls():
    conn, cur = open_db_connection()
    if request.method == 'POST':
        url = request.form['url']
        if not validators.url(url):
            flash('Некорректный URL!', 'danger')
            return redirect(url_for('index'))

        url = normalize_url(url)
        try:
            existing_url = check_url_exists(cur, url)
            if existing_url:
                flash('Страница уже существует', 'info')
                redirect_url = redirect(url_for('view_url', id=existing_url['id']))
            else:
                url_id = insert_new_url(cur, url)
                conn.commit()
                flash('URL успешно добавлен!', 'success')
                redirect_url = redirect(url_for('view_url', id=url_id))
        except Exception as e:
            conn.rollback()
            flash(f'Произошла ошибка при добавлении URL: {e}', 'danger')
            redirect_url = render_template('index.html'), 422
        finally:
            close_db_connection(conn, cur)
        return redirect_url

    urls = get_all_urls()
    close_db_connection(conn, cur)
    return render_template('list_urls.html', urls=urls)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url(id):
    conn, cur = open_db_connection()
    url = get_url_by_id(conn, id)
    if not url:
        flash('URL не найден!', 'danger')
        close_db_connection(conn, cur)
        return redirect(url_for('list_urls'))

    try:
        response = requests.get(url)
        response.raise_for_status()
        status_code = response.status_code
        parsed_content = fetch_and_parse_url(response.text)
    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        close_db_connection(conn, cur)
        return redirect(url_for('view_url', id=id))

    insert_url_check(conn, id, parsed_content)
    conn.commit()
    close_db_connection(conn, cur)
    flash('Проверка успешно запущена!', 'success')
    return redirect(url_for('view_url', id=id))


@app.route('/view_url/<int:id>')
def view_url(id):
    conn, cur = open_db_connection()
    url, checks = get_url_details(id)
    close_db_connection(conn, cur)
    if not url:
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
