from datetime import datetime
import requests
import os

from dotenv import load_dotenv
from flask import Flask
from flask import render_template
from flask import request
from flask import flash
from flask import url_for
from flask import redirect
from page_analyzer.url_validator import validate_and_normalize
from page_analyzer.repository import URLRepository
from page_analyzer.repository import URLCheckRepository
from page_analyzer.site_checker import SiteChecker
from page_analyzer.dao import URLCheck


load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
dsn = os.getenv("DATABASE_URL")
url_repository = URLRepository(dsn)
url_checks_repository = URLCheckRepository(dsn)


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/urls")
def add_url():
    req = request.form.to_dict()
    url_name = req.get("url")
    val_result = validate_and_normalize(url_name)
    status = val_result.get("status")
    if status == "error":
        flash("Некорректный URL", "error")
        return render_template("index.html"), 422
    normalized_url = val_result.get("value")
    resp = url_repository.save_url(normalized_url)
    saving_result = resp.get("status")
    if saving_result == "already exists":
        flash("Страница уже существует", "success")
        return redirect(url_for("url_details", id=resp.get("id")))
    flash("Страница успешно добавлена", "success")
    return redirect(url_for("url_details", id=resp.get("id")))


@app.get("/urls")
def urls():
    urls = url_repository.index()
    return render_template(
        "urls.html",
    urls=urls)


@app.get("/urls/<id>")
def url_details(id):
    url_detailed_info = url_repository.find_by_id(id)
    url_checks = url_checks_repository.index(id)

    return render_template(
        "url_checks.html",
        url=url_detailed_info,
        checks=url_checks)


@app.post("/urls/<id>/checks")
def check_url(id):
    url = url_repository.find_by_id(id)
    try:
        response = requests.get(url.name)
        response.raise_for_status()
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
        url_checks_repository.save(check)
        flash("Страница успешно проверена", "success")
        return redirect(url_for("url_details", id=id))
    except requests.HTTPError:
        flash("Произошла ошибка при проверке", "error")
        return render_template("url_checks.html")
