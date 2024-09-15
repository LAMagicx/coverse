from flask import Flask, render_template, send_file, redirect
from requests import session
from utils.db import create_authenticated_session, get_page

app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template("404.html"), 404


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/page/<int:page_id>")
def show_post(page_id: int):
    _ = create_authenticated_session()
    page = get_page(page_id=page_id)
    if page is not None:
        print(page)
        return render_template("page.html", page=page, zip=zip)
    else:
        return render_template("not_found.html", page_id=page_id)


@app.route("/sw.js")
def serve_sw():
    return send_file("static/sw.js", mimetype="application/javascript")


@app.route("/manifest.json")
def serve_manifest():
    return send_file("static/manifest.json", mimetype="application/manifest+json")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8085)
