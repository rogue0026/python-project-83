from datetime import datetime

import psycopg2
from psycopg2.extras import NamedTupleCursor
from page_analyzer.dao import URL
from page_analyzer.dao import URLCheck


class URLRepository:
    def __init__(self, conn_string: str):
        self.conn_string = conn_string

    def connect_to_db(self):
        return psycopg2.connect(self.conn_string)

    def index(self):
        sql = """
        SELECT
            id,
            name,
            created_at
        FROM urls
        ORDER BY created_at DESC;"""
        with self.connect_to_db() as conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                results = []
                for row in rows:
                    url = URL(row.id, row.name, row.created_at)
                    results.append(url)
                return results

    def find_by_id(self, id: int) -> URL:
        sql = """
        SELECT
            id,
            name,
            created_at
        FROM urls
        WHERE id = %s;"""

        with self.connect_to_db() as conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
                cur.execute(sql, (id,))
                row = cur.fetchone()
                return URL(row.id, row.name, row.created_at)

    def save_url(self, url_name: str) -> dict:
        sql = """
        INSERT INTO urls (name, created_at)
        VALUES (%s, %s) RETURNING id;"""
        with self.connect_to_db() as conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
                try:
                    cur.execute(sql, (url_name, datetime.now()))
                    row = cur.fetchone()
                    conn.commit()
                    return {
                        "status": "created",
                        "id": row.id
                    }
                except psycopg2.errors.UniqueViolation:
                    row = self.find_by_name(url_name)
                    return {
                        "status": "already exists",
                        "id": row.id
                    }

    def find_by_name(self, url_name: str) -> URL:
        sql = """
        SELECT
            id,
            name,
            created_at
        FROM urls
        WHERE name=%s;"""
        with self.connect_to_db() as conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
                cur.execute(sql, (url_name,))
                row = cur.fetchone()
                return URL(row.id, row.name, row.created_at)


class URLCheckRepository:
    def __init__(self, conn_string: str):
        self.conn_string = conn_string

    def connect_to_db(self):
        return psycopg2.connect(self.conn_string)

    def save(self, check: URLCheck):
        sql = """
        INSERT INTO url_checks(
            url_id, 
            status_code,
            h1,
            title,
            description,
            created_at)
        VALUES (%s, %s, %s, %s, %s, %s);"""
        with self.connect_to_db() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (check.url_id,
                                  check.status_code,
                                  check.h1,
                                  check.title,
                                  check.description,
                                  check.created_at))
            conn.commit()

    def index(self, url_id: int):
        sql = """
        SELECT
            id,
            url_id,
            status_code,
            h1,
            title,
            description,
            created_at
        FROM url_checks
        WHERE url_id=%s;"""
        with self.connect_to_db() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (url_id,))
                rows = cur.fetchall()
                results = []
                for row in rows:
                    check_info = URLCheck(row[0],
                                          row[1],
                                          row[2],
                                          row[3],
                                          row[4],
                                          row[5],
                                          row[6])
                    results.append(check_info)
                return results
