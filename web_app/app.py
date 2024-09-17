from flask import Flask, render_template, send_file, request, url_for, redirect
from requests import status_codes
from utils.db import fetch_access_token, make_request, refresh_token
from utils.schema import Page
import os
import time

app = Flask(__name__)

# Configuration
app.config["SECRET_KEY"] = os.environ.get("COVERSE_SECRET_KEY")
app.config["USERNAME"] = os.environ.get("COVERSE_USERNAME")
app.config["PASSWORD"] = os.environ.get("COVERSE_PASSWORD")
app.config["API_URL"] = os.environ.get("COVERSE_API_URL")
app.config["JWT_SECRET_KEY"], _ = fetch_access_token(
    app.config["API_URL"], app.config["USERNAME"], app.config["PASSWORD"]
)
app.config["JWT_TOKEN_LOCATION"] = ["headers"]


def get_page(page_id) -> Page | None:
    for _ in range(3):
        time.sleep(0.1)
        res = make_request(
            "GET", f"/v1/pages/{page_id}", token=app.config["JWT_SECRET_KEY"]
        )
        if res.status_code == 200:
            return Page.model_validate(res.json())
    return None


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.before_request
def check_token():
    app.config["JWT_SECRET_KEY"] = refresh_token(
        app.config["JWT_SECRET_KEY"],
        app.config["API_URL"],
        app.config["USERNAME"],
        app.config["PASSWORD"],
    )


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/page/<int:page_id>")
def show_post(page_id: int):
    prev_command_text = request.args.get("command", default="", type=str)
    page = get_page(page_id=page_id)
    if page is not None:
        if prev_command_text != "":
            return render_template(
                "page.html", page=page, command_text=prev_command_text, zip=zip
            )
        else:
            return render_template("page.html", page=page, zip=zip)
    else:
        return render_template("not_found.html", page_id=page_id)


@app.route("/config", methods=["GET", "POST"])
def update_config():
    if request.method == "GET":
        return render_template(
            "config.html",
            api_url=app.config["API_URL"],
            username=app.config["USERNAME"],
        )
    elif request.method == "POST":
        api_url = request.form.get("url")
        username = request.form.get("username")
        password = request.form.get("password")

        # Validation to ensure fields are not empty
        if not api_url or not username or not password:
            return render_template(
                "config.html",
                api_url=app.config["API_URL"],
                username=app.config["USERNAME"],
                error="All fields are required",
            )
        app.config["USERNAME"] = username
        app.config["PASSWORD"] = password
        app.config["API_URL"] = api_url
        try:
            new_token, status_code = fetch_access_token(
                app.config["API_URL"], app.config["USERNAME"], app.config["PASSWORD"]
            )
        except Exception as e:
            print(e)
            return render_template(
                "config.html",
                api_url=app.config["API_URL"],
                username=app.config["USERNAME"],
                error="Could not connect to server",
            )
        if status_code != 200:
            return render_template(
                "config.html",
                api_url=app.config["API_URL"],
                username=app.config["USERNAME"],
                error="username or password is incorrect",
            )
        elif new_token is not None:
            app.config["JWT_SECRET_KEY"] = new_token
            app.config["JWT_TOKEN_LOCATION"] = ["headers"]
            return redirect("/")


@app.route("/sw.js")
def serve_sw():
    return send_file("static/sw.js", mimetype="application/javascript")


@app.route("/manifest.json")
def serve_manifest():
    return send_file("static/manifest.json", mimetype="application/manifest+json")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8085)
