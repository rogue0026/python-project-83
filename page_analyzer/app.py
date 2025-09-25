import datetime
import os
import secrets
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)

from page_analyzer.parser import SiteChecker
from page_analyzer.url_validator import validate_url
from page_analyzer.urls import URLChecksRepository, UrlsRepository

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex(16)
dsn = os.getenv("DATABASE_URL")
urls_repository = UrlsRepository(dsn)
url_check_repository = URLChecksRepository(dsn)


@app.route("/")
def index():
    messages = get_flashed_messages(
        with_categories=True)
    return render_template(
        "index.html",
        messages=messages)


@app.get("/urls")
def urls_index():
    sites = urls_repository.index()
    return render_template(
        "urls.html",
        sites=sites
    )


@app.get("/urls/<id>")
def url_show(id):
    url_info = urls_repository.find(id)
    url_checks = url_check_repository.index(id)
    message = get_flashed_messages(with_categories=True)
    if url_info:
        return render_template(
            "url_info.html",
            site=url_info,
            checks=url_checks,
            messages=message)
    return "Not found", 404


@app.post("/urls")
def urls():
    form_data = request.form.to_dict()
    url_string = form_data.get("url")
    err_msg = validate_url(url_string)
    if err_msg:
        flash(err_msg, category="error")
        return redirect(url_for("index"))
    parsed_url = urlparse(url_string)
    status, msg = urls_repository.save(
        f"{parsed_url.scheme}://{parsed_url.hostname}",
        datetime.datetime.now())
    flash(msg, status)
    return redirect(url_for("index"))


@app.post("/urls/<id>/checks")
def create_new_check(id):
    url_info = urls_repository.find(id)
    url_address = url_info.get("name")
    try:
        response = requests.get(url_address)
        response.raise_for_status()
        checker = SiteChecker(response.text)
        h1_content = checker.check_for_h1()
        meta = checker.check_for_meta_description()
        title_content = checker.check_for_title()
        check_info = {
            "url_id": id,
            "status_code": response.status_code,
            "h1": h1_content if h1_content else "",
            "title": title_content if title_content else "",
            "description": meta if meta else ""
        }
        url_check_repository.save(check_info)
        flash("Страница успешно проверена", "success")
    except (requests.HTTPError, requests.ConnectionError):
        flash("Произошла ошибка при проверке", "error")
    return redirect(url_for("url_show", id=id))
