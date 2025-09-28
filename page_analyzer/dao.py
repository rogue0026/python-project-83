from datetime import datetime


class URL:
    def __init__(self,
                 id: int,
                 name: str,
                 created_at: datetime):
        self.id = id
        self.name = name
        self.created_at = created_at


class URLCheck:
    def __init__(self,
                 id: int,
                 url_id: int,
                 status_code: int,
                 h1: str,
                 title: str,
                 description: str,
                 created_at):
        self.id = id
        self.url_id = url_id
        self.status_code = status_code
        self.h1 = h1
        self.title = title
        self.description = description
        self.created_at = created_at
