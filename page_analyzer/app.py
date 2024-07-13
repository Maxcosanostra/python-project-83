import os
import logging
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse
import validators

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

logging.basicConfig(level=logging.INFO)

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='prefer', cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        logging.error(f"Ошибка подключения к базе данных: {e}")
        raise e

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/list_urls', methods=['GET', 'POST'])
def list_urls():
    conn = get_db_connection()
    if request.method == 'POST':
        url = request.form['url']
        logging.debug(f"Received URL: {url}")
        parsed_url = urlparse(url)
        if not validators.url(url) or not parsed_url.scheme or not parsed_url.netloc:
            logging.debug("URL validation failed")
            flash('Некорректный URL!', 'danger')
            return redirect(url_for('index'))

        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO urls (name) VALUES (%s) RETURNING id;", (url,))
            conn.commit()
            flash('URL успешно добавлен!', 'success')
        except psycopg2.IntegrityError:
            conn.rollback()
            flash('URL уже существует!', 'danger')
        finally:
            cursor.close()
        logging.debug("Redirecting to list_urls")
        return redirect(url_for('list_urls'))

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM urls ORDER BY created_at DESC;")
    urls = cursor.fetchall()
    cursor.close()
    conn.close()
    logging.debug(f"Fetched URLs: {urls}")
    return render_template('list_urls.html', urls=urls)

@app.route('/view_url/<int:id>')
def view_url(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM urls WHERE id = %s;", (id,))
    url = cursor.fetchone()
    cursor.close()
    conn.close()
    if url is None:
        flash('URL не найден!', 'danger')
        return redirect(url_for('list_urls'))
    return render_template('view_url.html', url=url)

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Server Error: {error}, Route: {request.url}")
    return "Internal Server Error", 500

@app.errorhandler(Exception)
def unhandled_exception(e):
    logging.error(f"Unhandled Exception: {e}, Route: {request.url}")
    return "Internal Server Error", 500

if __name__ == '__main__':
    app.run()
