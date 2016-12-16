from . import utils, models, authlib
from flask import Blueprint, abort, flash, jsonify, redirect, request, session, url_for

authenticator = authlib.SSOAuthenticator("http://localhost:5050")
blueprint = Blueprint("skel", __name__, url_prefix="/_")

@blueprint.before_app_request
def before_request():
    utils.set_csrf()
    models.database.connect()

    if "token" in session:
        try:
            sess = models.UserSession.get(token=session["token"])
            if not sess.valid:
                session.clear()
                flash("You have been logged out globally.")
        except models.UserSession.DoesNotExist:
            pass

@blueprint.after_app_request
def after_request(resp):
    models.database.close()
    return resp

@blueprint.route("/login/")
def login():
    return redirect(authenticator.request_url(url_for("skel.verify", _next=request.args.get("_next", "/"), _external=True)))

@blueprint.route("/verify/")
def verify():
    result = authenticator.token(request.args.get("token", ""), request.url)
    if result:
        session["username"] = result["user"]["name"]
        models.UserSession.create(token=result["id"], user=result["user"]["name"])

        flash("Login successful.")
        return redirect(request.args.get("_next", "/"))
    return "There was a problem with your authentication token; please try that again.", 401

@blueprint.route("/logout/")
def logout():
    if "username" in session:
        session.pop("username")
    if "token" in session:
        models.UserSession.update(valid=False) \
                          .where(models.UserSession.token == session["token"]) \
                          .execute()

    return redirect(request.args.get("/"))

@blueprint.route("/idplogout/")
def idplogout():
    n = models.UserSession.update(valid=False) \
                          .where(models.UserSession.token == request.args.get("token", "")) \
                          .execute()
    if not n:
        abort(404)

    return jsonify(ok=True)
