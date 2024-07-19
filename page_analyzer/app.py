import os
import requests
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse
import validators
from bs4 import BeautifulSoup

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


def get_db_connection():
    try:
        conn = psycopg2.connect(
            DATABASE_URL, sslmode='prefer', cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        raise e


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/list_urls', methods=['GET', 'POST'])
def list_urls():
    conn = get_db_connection()
    if request.method == 'POST':
        url = request.form['url']
        if not validators.url(url):
            flash('Некорректный URL!', 'danger')
            return redirect(url_for('index'))

        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            flash('Некорректный URL!', 'danger')
            return redirect(url_for('index'))

        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO urls (name) VALUES (%s) RETURNING id;", (url,)
            )
            url_id = cursor.fetchone()['id']
            conn.commit()
            flash('URL успешно добавлен!', 'success')
        except psycopg2.IntegrityError:
            conn.rollback()
            cursor.execute("SELECT id FROM urls WHERE name = %s;", (url,))
            url_id = cursor.fetchone()['id']
            flash('Страница уже существует', 'info')
        finally:
            cursor.close()
        return redirect(url_for('view_url', id=url_id))

    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT urls.id, urls.name,
               TO_CHAR(MAX(url_checks.created_at), 'YYYY-MM-DD')
               AS last_check_date,
               url_checks.status_code
        FROM urls
        LEFT JOIN url_checks ON urls.id = url_checks.url_id
        GROUP BY urls.id, url_checks.status_code
        ORDER BY urls.created_at DESC;
        """
    )
    urls = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('list_urls.html', urls=urls)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM urls WHERE id = %s;", (id,))
    url = cursor.fetchone()

    if url is None:
        flash('URL не найден!', 'danger')
        return redirect(url_for('list_urls'))

    try:
        response = requests.get(url['name'])
        response.raise_for_status()
        status_code = response.status_code

        soup = BeautifulSoup(response.text, 'html.parser')
        h1 = soup.find('h1').text if soup.find('h1') else None
        title = soup.title.string if soup.title else None
        description = None
        if soup.find('meta', attrs={'name': 'description'}):
            description = soup.find(
                'meta', attrs={'name': 'description'}
            )['content']

    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('view_url', id=id))

    cursor.execute(
        """
        INSERT INTO url_checks (
            url_id, status_code, h1, title, description, created_at
        ) VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)
        RETURNING id;
        """,
        (id, status_code, h1, title, description)
    )
    conn.commit()
    cursor.close()
    conn.close()
    flash('Проверка успешно запущена!', 'success')
    return redirect(url_for('view_url', id=id))


@app.route('/view_url/<int:id>')
def view_url(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, name, TO_CHAR(created_at, 'YYYY-MM-DD') AS created_at
        FROM urls WHERE id = %s;
        """,
        (id,)
    )
    url = cursor.fetchone()
    cursor.execute(
        """
        SELECT id, status_code, h1, title, description,
               TO_CHAR(created_at, 'YYYY-MM-DD') AS created_at
        FROM url_checks
        WHERE url_id = %s
        ORDER BY created_at DESC;
        """,
        (id,)
    )
    checks = cursor.fetchall()
    cursor.close()
    conn.close()
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
