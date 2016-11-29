from . import utils, models
from flask import Blueprint, flash, redirect, request, session, url_for

authenticator = utils.SSOAuthenticator("https://auth.fwilson.me")
blueprint = Blueprint("skel", __name__, url_prefix="/_")

@blueprint.before_app_request
def before_request():
    utils.set_csrf()
    models.database.connect()

@blueprint.after_app_request
def after_request(resp):
    models.database.close()
    return resp

@blueprint.route("/login/")
def login():
    return redirect(authenticator.request_url(url_for("skel.verify", _next=request.args.get("_next", "/"), _external=True)))

@blueprint.route("/verify/")
def verify():
    result = authenticator.verify(request.args.get("token", ""), request.url)
    if result:
        session["username"] = result["username"]
        flash("Login successful.")
        return redirect(request.args.get("_next", "/"))
    return "There was a problem with your authentication token; please try that again.", 401

@blueprint.route("/logout/")
def logout():
    if "username" in session:
        session.pop("username")
    return redirect(request.args.get("/"))
