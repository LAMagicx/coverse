import os
from typing import Optional, List
from pydantic import BaseModel

from flask import Flask, render_template, send_file, request, url_for, redirect, session, jsonify
from flask_session import Session
from requests import status_codes

import hashlib

from db import SurrealDB, SurrealTable

SurrealDB.connect("http://coverse-db:8000",
                  os.environ.get("SURREAL_USERNAME"),
                  os.environ.get("SURREAL_PASSWORD"),
                  "test",
                  "test")

class Command(BaseModel):
    name: str
    text: str
    page: int | str
    required: List[Optional[int | str]] = []

class Page(SurrealTable):
    title: str
    text: str
    limit: int
    commands: List[Command] = []
                  

app = Flask(__name__)

app.config["SESSION_TYPE"] = "cachelib"
Session(app)


@app.errorhandler(404)
def page_not_found(e):
    print(f"404: {e}")
    return render_template("404.html"), 404

@app.before_request
def check_token():
    if "visits" not in session:
        session["visits"] = set()

    if "user_id" not in session.keys():
        ua = request.headers.get("User-Agent")
        ip = request.access_route[-1]
        uid = f"{ip}_{hashlib.sha1(ua.encode('utf-8')).hexdigest()[:8]}"
        session["user_id"] = uid


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/page/<int:page_id>", methods=["GET"])
def show_page(page_id: int):
    page = Page.select(page_id)
    if page is None:
        session["visits"].add(str(page_id))
        return render_template('not_found.html', page_id=page_id)

    shows = [len(session["visits"].intersection(command.required)) > 0 if len(command.required) > 0 else True for command in page.commands]

    return render_template('page.html', page=page, zip=zip, shows=shows)


def process_page_form(form_data, page_id) -> tuple[Page | None, str | None]:
    """Process form data and create/update a Page object
    
    Returns:
        tuple: (Page object or None, error message or None)
    """
    try:
        # Process commands
        commands = []
        if 'commands[0][name]' in form_data:
            command_count = sum(1 for key in form_data if key.startswith('commands[') and key.endswith('][name]'))
            
            for i in range(command_count):
                name = form_data.get(f'commands[{i}][name]', '')
                text = form_data.get(f'commands[{i}][text]', '')
                page_dest = form_data.get(f'commands[{i}][page]', '')
                required_str = form_data.get(f'commands[{i}][required]', '')
                
                # Convert required string to list
                required = [r.strip() for r in required_str.split(',')] if required_str else []
                
                commands.append(Command(
                    name=name,
                    text=text,
                    page=page_dest,
                    required=required
                ))
        
        page = Page(
            id=page_id,
            title=form_data.get('title', ''),
            text=form_data.get('text', ''),
            limit=int(form_data.get('limit', 3)),
            commands=commands
        )
        page.create()
        return page, None
            
    except Exception as e:
        return None, f"Failed to create page: {str(e)}"

@app.route("/create/<int:page_id>", methods=["GET", "POST"])
def create(page_id: int):
    # Check if page exists for GET requests
    if request.method == "GET":
        page = Page.select(page_id)
        if page is not None:
            # Page exists, redirect to view it
            return redirect(url_for('show_page', page_id=page_id))
        if page_id < 10 and page_id != 5:
            return render_template('error.html', error=f"Page {page_id} is reserved. Please choose another page.")

        return render_template('create.html', page_id=page_id)
    
    # Handle POST request
    if request.method == "POST":
        # Process form data
        form_data = {
            key: value[0] if len(value) == 1 else value
            for key, value in request.form.items(multi=True)
        }
        
        # Process the form data
        page, error = process_page_form(form_data, page_id)

        if page is None:
            return render_template('error.html', error=f"Page error: {error} page_id")

        print(page)
        if page.id.record_id < 10:
            # pages < 10 are reserved show error and try again
            return render_template('error.html', error=f"Page {page_id} is reserved. Please choose another page.")

        
        # Return JSON response if it's an HTMX request
        if request.headers.get('HX-Request') == 'true':
            if error:
                return jsonify({'success': False, 'message': error})
            else:
                return redirect(url_for('show_page', page_id=page.id))
        
        # Regular form submission (full page reload)
        if page:
            return redirect(url_for('show_page', page_id=page_id))
        else:
            # If there was an error, show the form again with the error message
            return render_template('create.html', page_id=page_id, error=error)
        

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=8085, use_reloader=True)
