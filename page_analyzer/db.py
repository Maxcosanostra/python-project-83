import psycopg2
from psycopg2.extras import NamedTupleCursor


def connect_db(app):
    return psycopg2.connect(app.config['DATABASE_URL'])


def commit(conn):
    conn.commit()


def close(conn):
    conn.close()


def get_url(conn, url_id):
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            'SELECT * FROM urls WHERE id = %s ORDER BY id DESC;',
            (url_id,)
        )
        return curs.fetchone()


def get_urls(conn):
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            'SELECT * FROM urls ORDER BY id DESC;'
        )
        return curs.fetchall()


def insert_url(conn, url):
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            'INSERT INTO urls (name) VALUES (%s) '
            'RETURNING id;',
            (url,)
        )
        return curs.fetchone().id


def insert_url_check(conn, url_id, page_data):
    with conn.cursor() as curs:
        curs.execute(
            'INSERT INTO url_checks (url_id, status_code, h1, title, '
            'description) VALUES (%s, %s, %s, %s, %s);',
            (url_id, page_data['status_code'], page_data['h1'],
             page_data['title'], page_data['description'])
        )


def get_checks_by_url_id(conn, url_id):
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            'SELECT * FROM url_checks '
            'WHERE url_id = %s ORDER BY id DESC;',
            (url_id,)
        )
        return curs.fetchall()


def get_urls_with_last_check_date_and_status_code(conn):
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            'SELECT DISTINCT ON (u.id) '
            'u.id, u.name, '
            'uc.created_at AS last_check_date, '
            'uc.status_code AS last_status_code '
            'FROM urls u '
            'LEFT JOIN url_checks uc ON u.id = uc.url_id '
            'ORDER BY u.id DESC, uc.created_at DESC;'
        )
        return curs.fetchall()


def get_url_by_name(conn, name):
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            'SELECT * FROM urls WHERE name = %s;',
            (name,)
        )
        return curs.fetchone()
