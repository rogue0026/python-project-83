import psycopg2
from psycopg2.extras import NamedTupleCursor
from psycopg2 import pool
from datetime import datetime


def init_pool(dsn: str) -> pool.SimpleConnectionPool:
    return pool.SimpleConnectionPool(5, 10, dsn)


class UrlsRepository:
    def __init__(self, dsn: str):
        self.dsn = dsn

    def _connect_to_db(self):
        return psycopg2.connect(self.dsn)

    def save(self, url: str, created_at) -> tuple:
        message = tuple()
        with self._connect_to_db() as db_connection:
            with db_connection.cursor() as cursor:
                try:
                    sql_query = "INSERT INTO urls (name, created_at) VALUES (%s, %s);"
                    cursor.execute(sql_query, (url, created_at))
                    db_connection.commit()
                    message = ("success", "URL added successfully")
                except psycopg2.errors.UniqueViolation:
                    message = ("error", "URL already exists")
                    db_connection.rollback()
        return message

    def index(self) -> list[dict]:
        results = []
        with self._connect_to_db() as db_connection:
            with db_connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
                sql_query = """
                            select urls.id, \
                                   name, \
                                   url_checks.status_code, \
                                   max(url_checks.created_at) as last_check
                            from urls
                                     left join url_checks on urls.id = url_checks.url_id
                            group by urls.id, name, status_code
                            order by urls.id desc"""
                cursor.execute(sql_query)
                rows = cursor.fetchall()
                for row in rows:
                    url_info = {
                        "id": row.id,
                        "name": row.name,
                        "status_code": row.status_code if row.status_code is not None else "",
                        "last_check": row.last_check.date() if row.last_check is not None else ""
                    }
                    results.append(url_info)
        return results

    def find(self, url_id) -> dict:
        result = {}
        with self._connect_to_db() as db_connection:
            with db_connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
                sql_query = "SELECT id, name, created_at FROM urls WHERE id = %s;"
                cursor.execute(sql_query, (url_id,))
                row = cursor.fetchone()
                result["id"] = row.id
                result["name"] = row.name
                result["created_at"] = row.created_at.date()
        return result


class URLChecksRepository:
    def __init__(self, dsn: str):
        self.dsn = dsn

    def _connect_to_db(self):
        return psycopg2.connect(self.dsn)

    def save(self, url_id: int):
        with self._connect_to_db() as db_connection:
            sql_query = "INSERT into url_checks(url_id, created_at) VALUES (%s, %s);"
            with db_connection.cursor() as cursor:
                cursor.execute(sql_query, (url_id, datetime.now()))
            db_connection.commit()

    def index(self, url_id) -> list[dict]:
        results = []
        with self._connect_to_db() as db_connection:
            sql_query = "SELECT id, url_id, status_code, h1, title, description, created_at FROM url_checks WHERE url_id=%s;"
            with db_connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
                cursor.execute(sql_query, (url_id,))
                rows = cursor.fetchall()
                for row in rows:
                    check = {
                        "id": row.id,
                        "url_id": row.url_id,
                        "status_code": row.status_code if row.status_code is not None else "",
                        "h1": row.h1 if row.h1 is not None else "",
                        "title": row.title if row.title is not None else "",
                        "description": row.description if row.description is not None else "",
                        "created_at": row.created_at.date()
                    }
                    results.append(check)
        return results

    def get_last_check_info(self, url_id) -> dict | None:
        last_check_info = None
        with self._connect_to_db() as db_connection:
            sql_query = "SELECT status_code, created_at FROM url_checks WHERE url_id=%s ORDER BY created_at DESC limit 1;"
            with db_connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
                cursor.execute(sql_query, (url_id,))
                row = cursor.fetchone()
                last_check_info = {
                    "status_code": row.status_code if row.status_code is not None else "",
                    "created_at": row.created_at.date()
                }
        return last_check_info
