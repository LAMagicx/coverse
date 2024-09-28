from flask import Flask, render_template, send_file, request, url_for, redirect
from requests import status_codes
from utils.db import fetch_access_token, make_request, refresh_token
from utils.schema import Page, CreatePage, Command
from pydantic import ValidationError
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


def post_page(page: CreatePage):
    res = make_request(
        "POST",
        f"/v1/pages/{page.id}",
        data=page.model_dump(),
        token=app.config["JWT_SECRET_KEY"],
    )
    if res.status_code == 201:
        # success
        return redirect(f"/page/{page.id}")
    if res.status_code == 422:
        # unprossable entity
        return render_template(
            "create.html",
            page_id=page.id,
            error="Error in the page. Your text is probably too long.",
            page=page,
        )
    elif res.status_code == 409:
        # page exists
        return render_template("not_found.html", page_id=page.id)
    else:
        # other error
        return render_template("404.html"), res.status_code


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
def show_page(page_id: int):
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


@app.route("/create/<int:page_id>", methods=["GET", "POST"])
def create(page_id: int):
    if request.method == "POST":
        form_data = request.form.to_dict(flat=False)

        # {'id': ['0'], 'title': ['werew'], 'text': ['qwrqwr'], 'limit': ['2'], 'commands[0][name]': ['qwrqwr'], 'commands[0][text]': ['qwrqwr'], 'commands[0][page]': ['1'], 'commands[0][required]': [''], 'commands[1][name]': ['qwrqwr'], 'commands[1][text]': ['qwrqrw'], 'commands[1][page]': ['2'], 'commands[1][required]': ['']}
        # Parse commands from form data
        commands = []
        for i in range(int(form_data.get("limit", ["0"])[0])):
            if f"commands[{i}][name]" not in form_data.keys():
                break
            try:
                command = Command(
                    name=form_data[f"commands[{i}][name]"][0],
                    text=form_data[f"commands[{i}][text]"][0],
                    page=form_data[f"commands[{i}][page]"][0],
                    required=[
                        req.strip()
                        for req in form_data.get(f"commands[{i}][required]", [""])[
                            0
                        ].split(",")
                        if req.strip().isdecimal()
                    ],
                )
                commands.append(command)
            except ValidationError as e:
                print(f"Error in command {i + 1}: {e}", "error")
                return render_template("create.html", page_id=page_id, error=e)

        try:
            page = CreatePage(
                id=page_id,
                title=form_data["title"][0],
                text=form_data["text"][0],
                limit=form_data["limit"][0],
                commands=commands,
            )
            return post_page(page)
        except ValidationError as e:
            print(f"Error in page data: {e}", "error")
            return render_template("create.html", page_id=page_id, error=e)

    return render_template("create.html", page_id=page_id)


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
