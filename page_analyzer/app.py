from urllib.parse import urlparse
import os
from datetime import datetime
import requests
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from page_analyzer.dto import URLCheck
from page_analyzer.repository import URLCheckRepository, URLRepository
from page_analyzer.site_checker import SiteChecker
from page_analyzer.url_validator import validate_url


load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
dsn = os.getenv("DATABASE_URL")
url_repository = URLRepository(dsn)
url_checks_repository = URLCheckRepository(dsn)


@app.route("/")
def index():
    return render_template("index.html"), 200


@app.post("/urls")
def add_url():
    req = request.form.to_dict()
    url_string = req.get("url")
    val_result = validate_url(url_string)
    status = val_result.get("status")
    if status == "error":
        flash("Некорректный URL", "error")
        return render_template("index.html"), 422
    parsed = urlparse(url_string)
    normalized_url = f"{parsed.scheme}://{parsed.hostname}"
    with url_repository as repo:
        resp = repo.save_url(normalized_url)
    saving_result = resp.get("status")
    if saving_result == "already exists":
        flash("Страница уже существует", "success")
        return redirect(url_for("url_details", id=resp.get("id")))
    flash("Страница успешно добавлена", "success")
    return redirect(url_for("url_details", id=resp.get("id")))


@app.get("/urls")
def urls():
    with url_repository as repo:
        urls = repo.index()
    return render_template(
        "urls.html",
    urls=urls), 200


@app.get("/urls/<id>")
def url_details(id):
    with url_repository as url_repo:
        url_detailed_info = url_repo.find_by_id(id)
    with url_checks_repository as url_checks_repo:
        url_checks = url_checks_repo.index(id)
    return render_template(
        "url_checks.html",
        url=url_detailed_info,
        checks=url_checks), 200


@app.post("/urls/<id>/checks")
def check_url(id):
    with url_repository as url_repo:
        url = url_repo.find_by_id(id)
    response = None
    try:
        response = requests.get(url.name)
        response.raise_for_status()
    except (requests.HTTPError, requests.exceptions.ConnectionError):
        flash("Произошла ошибка при проверке", "error")
        return redirect(url_for("url_details", id=id))
    page_content = response.text
    checker = SiteChecker(page_content)
    h1 = checker.check_for_h1()
    title = checker.check_for_title()
    description = checker.check_for_meta_description()
    check = URLCheck(id=None,
                     url_id=url.id,
                     status_code=response.status_code,
                     h1=h1,
                     title=title,
                     description=description,
                     created_at=datetime.now())
    with url_checks_repository as url_checks_repo:
        url_checks_repo.save(check)
    flash("Страница успешно проверена", "success")
    return redirect(url_for("url_details", id=id))
