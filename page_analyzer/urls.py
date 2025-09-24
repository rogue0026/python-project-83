import psycopg2
from psycopg2.extras import NamedTupleCursor
from psycopg2 import pool


class UrlsRepository:
    def __init__(self, dsn: str):
        conn_pool = pool.SimpleConnectionPool(5, 10, dsn)
        self.conn_pool = conn_pool

    def save(self, url: str, created_at) -> tuple:
        db_connection = self.conn_pool.getconn()
        message = tuple()
        try:
            if db_connection:
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
        finally:
            self.conn_pool.putconn(db_connection)

    def index(self) -> list:
        db_connection = self.conn_pool.getconn()
        result = None
        try:
            if db_connection:
                with db_connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
                    sql_query = "SELECT id, name, created_at FROM urls ORDER BY created_at DESC;"
                    cursor.execute(sql_query)
                    result = cursor.fetchall()
            return result
        finally:
            self.conn_pool.putconn(db_connection)

    def find(self, url_id) -> dict:
        db_connection = self.conn_pool.getconn()
        result = {}
        try:
            if db_connection:
                with db_connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
                    sql_query = "SELECT id, name, created_at FROM urls WHERE id = %s;"
                    cursor.execute(sql_query, (url_id,))
                    row = cursor.fetchone()
                    result["id"] = row.id
                    result["name"] = row.name
                    result["created_at"] = row.created_at
            return result
        finally:
            self.conn_pool.putconn(db_connection)
