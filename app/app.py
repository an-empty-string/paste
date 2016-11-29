import os
import playhouse.db_url

from . import utils, models, skel
from flask import Flask, flash, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.getenv("SECRET", os.urandom(32))

app.register_blueprint(skel.blueprint)

@app.route("/", methods=["GET", "POST"])
@utils.require_csrf
@utils.require_login
def index():
    if request.method == "GET":
        pastes = models.Paste.select() \
                             .where(models.Paste.author == session["username"]) \
                             .order_by(models.Paste.created)

        return render_template("new_paste.html", pastes=pastes)

    title = request.form.get("title", "Untitled paste")
    text = request.form.get("text", "")

    paste = models.Paste.create(title=title, text=text, author=session["username"])
    return redirect(url_for("show_paste", slug=paste.slug))

@app.route("/api/key/")
@utils.require_login
def get_key():
    key = models.APIAccess.get_or_create(user=session["username"])[0].key
    return render_template("api_key.html", key=key)

@app.route("/api/create/", methods=["POST"])
def api_create():
    try:
        user = models.APIAccess.get(key=request.args.get("key", "")).user
    except models.APIAccess.DoesNotExist:
        return "Your API key is invalid.", 403

    paste = models.Paste.create(title=request.args.get("title", "Untitled paste"), text=request.get_data(), author=user)
    return url_for("show_paste", slug=paste.slug, _external=True)

@app.route("/p/<slug>/delete/", methods=["GET", "POST"])
@utils.require_csrf
@utils.require_login
def delete_paste(slug):
    try:
        paste = models.Paste.get(slug=slug, author=session["username"])
    except Paste.DoesNotExist:
        return "Couldn't find that paste.", 404

    if request.method == "GET":
        return render_template("confirm_delete.html", paste=paste)

    paste.delete_instance()
    flash("Paste deleted.")
    return redirect(url_for("index"))

@app.route("/p/<slug>/rename/", methods=["GET", "POST"])
@utils.require_csrf
@utils.require_login
def rename_paste(slug):
    try:
        paste = models.Paste.get(slug=slug, author=session["username"])
    except Paste.DoesNotExist:
        return "Couldn't find that paste.", 404

    if request.method == "GET":
        return render_template("rename_paste.html", paste=paste)

    paste.title = request.form.get("title", "")
    paste.save()
    flash("Paste renamed.")
    return redirect(url_for("show_paste", slug=slug))

@app.route("/p/<slug>/")
def show_paste(slug):
    try:
        paste = models.Paste.get(slug=slug)
    except models.Paste.DoesNotExist:
        return "Couldn't find that paste.", 404

    return render_template("show_paste.html", paste=paste)

@app.route("/p/<slug>/raw/")
def raw_paste(slug):
    try:
        paste = models.Paste.get(slug=slug)
    except models.Paste.DoesNotExist:
        return "Couldn't find that paste.", 404
    return paste.text, 200, {"Content-Type": "text/plain; charset=utf-8"}
