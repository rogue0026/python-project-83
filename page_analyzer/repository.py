from datetime import datetime

import psycopg2
from psycopg2.extras import NamedTupleCursor

from page_analyzer.dto import URL, URLCheck


class URLRepository:
    def __init__(self, conn_string: str):
        self.__conn_string = conn_string

    def __enter__(self):
        self.__db_connection = psycopg2.connect(self.__conn_string)
        self.__cursor = self.__db_connection.cursor(
            cursor_factory=NamedTupleCursor)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__cursor.close()
        self.__db_connection.commit()
        self.__db_connection.close()

    def index(self) -> list[dict]:
        sql = """
            SELECT urls.id, 
                urls.name, 
                url_checks.status_code, 
                max(url_checks.created_at) as last_check
            FROM urls
            LEFT JOIN url_checks ON urls.id = url_checks.url_id
            GROUP BY urls.id, urls.name, urls.created_at, url_checks.status_code
            ORDER BY urls.created_at DESC;
        """
        self.__cursor.execute(sql)
        rows = self.__cursor.fetchall()
        results = []
        for row in rows:
            for row in rows:
                status_code = row.status_code
                if status_code is None:
                    status_code = ""
                last_check = row.last_check
                if last_check is None:
                    last_check = ""
                else:
                    last_check = last_check.date()
                info = {
                    "id": row.id,
                    "name": row.name,
                    "status_code": status_code,
                    "last_check": last_check
                }
                results.append(info)
            return results

    def find_by_id(self, id: int) -> URL:
        sql = """
        SELECT
            id,
            name,
            created_at
        FROM urls
        WHERE id = %s;"""

        self.__cursor.execute(sql, (id,))
        row = self.__cursor.fetchone()
        return URL(row.id, row.name, row.created_at)

    def find_by_name(self, name: str) -> URL:
        sql = """
            SELECT
                id, 
                name, 
                created_at
            FROM urls
            WHERE name = %s;"""

        self.__cursor.execute(sql, (name,))
        row = self.__cursor.fetchone()
        return URL(row.id, row.name, row.created_at)

    def save_url(self, url_name: str) -> dict:
        sql = """
        INSERT INTO urls (name, created_at)
        VALUES (%s, %s)
        RETURNING id;"""
        result = {}
        try:
            self.__cursor.execute(sql, (url_name, datetime.now()))
            row = self.__cursor.fetchone()
            result = {
                "status": "created",
                "id": row.id
            }
        except psycopg2.errors.UniqueViolation:
            self.__db_connection.rollback()
            row = self.find_by_name(url_name)
            result = {
                "status": "already exists",
                "id": row.id
            }
        return result


class URLCheckRepository:
    def __init__(self, conn_string: str):
        self.__conn_string = conn_string

    def __enter__(self):
        self.__db_connection = psycopg2.connect(self.__conn_string)
        self.__cursor = self.__db_connection.cursor(
            cursor_factory=NamedTupleCursor)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__cursor.close()
        self.__db_connection.commit()
        self.__db_connection.close()

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
        self.__cursor.execute(sql, (check.url_id,
                                    check.status_code,
                                    check.h1,
                                    check.title,
                                    check.description,
                                    check.created_at))

    def index(self, url_id) -> list[URLCheck]:
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
        WHERE url_id = %s;"""
        self.__cursor.execute(sql, (url_id,))
        rows = self.__cursor.fetchall()
        results = []
        for row in rows:
            status_code = row.status_code if row.status_code else ""
            h1 = row.h1 if row.h1 else ""
            title = row.title if row.title else ""
            description = row.description if row.description else ""
            url_check = URLCheck(row.id,
                                 row.url_id,
                                 status_code,
                                 h1,
                                 title,
                                 description,
                                 row.created_at)
            results.append(url_check)
        return results
