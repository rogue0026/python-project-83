import datetime
import os
from urllib.parse import urlparse
import secrets
import validators
from dotenv import load_dotenv
from page_analyzer.urls import UrlsRepository
from page_analyzer.urls import URLChecksRepository
from page_analyzer.urls import init_pool
from flask import (
    Flask,
    render_template,
    request,
    url_for,
    redirect,
    flash,
    get_flashed_messages
)


load_dotenv()


def app():
    application = Flask(__name__)
    application.config["SECRET_KEY"] = secrets.token_hex(16)
    dsn = os.getenv("DATABASE_URL")
    conn_pool = init_pool(dsn)
    urls_repository = UrlsRepository(conn_pool)
    url_check_repository = URLChecksRepository(conn_pool)


    @application.route("/")
    def index():
        messages = get_flashed_messages(
            with_categories=True)
        return render_template(
            "index.html",
            messages=messages)


    @application.get("/urls")
    def urls_index():
        sites = urls_repository.index()

        return render_template(
            "urls.html",
            sites=sites
        )

    @application.get("/urls/<id>")
    def url_show(id):
        url_info = urls_repository.find(id)
        url_checks = url_check_repository.index(id)
        if url_info:
            return render_template(
                "url_info.html",
                site=url_info,
                checks=url_checks)


    @application.post("/urls")
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


    @application.post("/urls/<id>/checks")
    def create_new_check(id):
        url_check_repository.save(id)
        return redirect(url_for("url_show", id=id))

    return application


def validate_url(url_string: str) -> str | None:
    if len(url_string) == 0:
        return "URL string can't be blank"
    if validators.url(url_string) is not True:
        return "Invalid URL format"
    return None

