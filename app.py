import os

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
    make_response,
)

from functools import wraps

app = Flask(__name__)


def auth(f):
    """
    If you dont use the "wraps" decorator, all the functionswhere you use it, will have myRouteFunc.__name__ = "wrapper" instead of the real name (myRouteFunc).
    Flasks needs the real function name to know which function to call on each route, otherwise it will throw an error:
        AssertionError: View function mapping is overwriting an existing endpoint function: check_authentication
    """

    @wraps(f)
    def check_authentication(*args, **kwargs):
        # REQUEST SHOULD HAVE A HEADER LIKE:
        # ('Authorization', 'Basic YXNkZjrDsWxrasOxaw==')

        auth = request.authorization
        if auth and auth.username == "Dan" and len(auth.password) > 3:
            return f(*args, **kwargs)
        return authenticate()
        # NOTE: firefox only clears the WWW-Authenticate cache in the same session after a 403 Forbidden error
        # Chrome does it with a 403 or 401 Not authorized

    return check_authentication


def authenticate():
    # NOTE: without the 401 status code the WWW-Authenticate doesn't work!
    res = make_response("<h1>Not authorized!</h1>", 401)
    res.headers["WWW-Authenticate"] = 'Basic realm="Login Required"'
    return res


@app.route("/headers")
def headers():
    res = make_response("<h1>Hello</h1>", 201)
    res.headers["mycustomehader"] = True
    res.headers["dict"] = {"asdf": 1234}
    print(res.headers.__dict__)
    return res


@app.route("/error")
def error():
    return make_response("Not found...", 500)


@app.route("/echo")
def echo():
    print(request.__dict__)
    return "Watch the server", 203


@app.route("/private")
@auth
def private():
    return "<h1>Succesful login</h1>"


@app.route("/other")
@auth
def otherprivate():
    return "<h1>Succesful login?????</h1>"


@app.route("/")
def index():
    print("Request for index page received")
    return render_template("index.html")


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.route("/hello", methods=["POST"])
def hello():
    name = request.form.get("name")

    if name:
        print("Request for hello page received with name=%s" % name)
        return render_template("hello.html", name=name)
    else:
        print(
            "Request for hello page received with no name or blank name -- redirecting"
        )
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run()
