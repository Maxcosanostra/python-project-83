import os
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

conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/list_urls', methods=['GET', 'POST'])
def list_urls():
    if request.method == 'POST':
        url = request.form['url']
        parsed_url = urlparse(url)
        if not validators.url(url) or not parsed_url.scheme or not parsed_url.netloc:
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
        return redirect(url_for('list_urls'))

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM urls ORDER BY created_at DESC;")
    urls = cursor.fetchall()
    return render_template('list_urls.html', urls=urls)

@app.route('/view_url/<int:id>')
def view_url(id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM urls WHERE id = %s;", (id,))
    url = cursor.fetchone()
    if url is None:
        flash('URL не найден!', 'danger')
        return redirect(url_for('list_urls'))
    return render_template('view_url.html', url=url)

if __name__ == '__main__':
    app.run()
