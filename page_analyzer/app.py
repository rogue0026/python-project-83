from urllib.error import HTTPError

import requests
from dotenv import load_dotenv
from flask import Flask
from flask import render_template
from flask import request
from flask import flash
from os import getenv
from secrets import token_hex
from page_analyzer.url_validator import validate_and_parse
from page_analyzer.urls import UrlsRepository
from page_analyzer.urls import URLChecksRepository
from page_analyzer.parser import SiteChecker
load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = token_hex(16)
dsn = getenv('DATABASE_URL')

urls_repository = UrlsRepository(dsn)
url_checks_repository = URLChecksRepository(dsn)

@app.route("/")
def index():
    return render_template("index.html"), 200


@app.get("/urls")
def urls_index():
    sites = urls_repository.index()
    return render_template(
        "urls.html",
        sites=sites), 200


@app.post("/urls")
def add_url():
    req = request.form.to_dict()
    url = req.get("url")
    result = validate_and_parse(url)
    if "error" in result:
        flash("Некорректный URL", "error")
        return render_template("index.html"), 422
    hostname = result.get("success")
    category, msg = urls_repository.save(hostname)
    flash(msg, category)
    return render_template("index.html"), 200


@app.get("/urls/<id>")
def url_checks_index(id):
    url_info = urls_repository.find(id)
    url_checks = url_checks_repository.index(id)
    return render_template(
        "url_checks.html",
        url=url_info,
        checks=url_checks), 200


@app.post("/urls/<id>/checks")
def check_url(id):
    url_info = urls_repository.find(id)
    try:
        resp = requests.get(url_info["name"])
        resp.raise_for_status()
        checker = SiteChecker(resp.text)
        title = checker.check_for_title()
        h1 = checker.check_for_h1()
        meta = checker.check_for_meta_description()
        check_info = {
            "url_id": url_info["id"],
            "status_code": resp.status_code,
            "h1": h1,
            "title": title,
            "description": meta
        }
        url_checks_repository.save(check_info)
        checks = url_checks_repository.index(id)
        return render_template(
            "url_checks.html", url=url_info, checks=checks), 200
    except (requests.HTTPError, requests.ConnectionError):
        flash("Произошла ошибка при проверке", "error")
        checks = url_checks_repository.index(id)
        return render_template(
            "url_checks.html", url=url_info, checks=checks), 500