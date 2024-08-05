import psycopg2
from psycopg2.extras import NamedTupleCursor


def connect_db(app):
    return psycopg2.connect(app.config['DATABASE_URL'])


def commit(conn):
    conn.commit()


def close(conn):
    conn.close()


def insert_url(conn, url):
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            'INSERT INTO urls (name) VALUES (%s) '
            'RETURNING id;',
            (url,)
        )
        return curs.fetchone().id


def get_url_by_name(conn, name):
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            'SELECT * FROM urls WHERE name = %s;',
            (name,)
        )
        return curs.fetchone()


def get_url(conn, url_id):
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            'SELECT * FROM urls WHERE id = (%s);',
            (url_id,)
        )
        return curs.fetchone()


def get_urls(conn):
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            """
            SELECT urls.id, urls.name,
                   MAX(url_checks.created_at) AS last_check_date,
                   url_checks.status_code
            FROM urls
            LEFT JOIN url_checks ON urls.id = url_checks.url_id
            GROUP BY urls.id, url_checks.status_code
            ORDER BY urls.created_at DESC;
            """
        )
        return curs.fetchall()


def insert_url_check(conn, url_id, page_data):
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            """
            INSERT INTO url_checks (
                url_id, status_code, h1, title, description, created_at
            ) VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id;
            """,
            (
                url_id,
                page_data['status_code'],
                page_data['h1'],
                page_data['title'],
                page_data['description']
            )
        )
        return curs.fetchone().id


def get_url_checks(conn, url_id):
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            """
            SELECT id, status_code, h1, title, description, created_at
            FROM url_checks
            WHERE url_id = %s
            ORDER BY created_at DESC;
            """,
            (url_id,)
        )
        return curs.fetchall()
