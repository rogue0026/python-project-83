import psycopg2
from psycopg2.extras import NamedTupleCursor


class UrlsRepository:
    def __init__(self, dsn: str):
        connection = psycopg2.connect(dsn)
        self.db_connection = connection


    def save(self, url: str, created_at) -> tuple:
        sql_query = "INSERT INTO urls (name, created_at) VALUES (%s, %s);"
        message = tuple()
        with self.db_connection.cursor() as cursor:
            try:
                cursor.execute(sql_query, (url, created_at))
                self.db_connection.commit()
                message = ("success", "URL added successfully")
            except psycopg2.errors.UniqueViolation:
                message = ("error", "URL already exists")
                self.db_connection.rollback()
        self.db_connection.commit()
        return message


    def index(self) -> list:
        sql_query = "SELECT id, name, created_at FROM urls ORDER BY created_at DESC;"
        sites = None
        with self.db_connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute(sql_query)
            sites = cursor.fetchall()
        self.db_connection.commit()
        return sites
