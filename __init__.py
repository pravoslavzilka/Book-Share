from flask import Flask, render_template, redirect, url_for
from blueprints.admin.__init__ import admin_bp
from blueprints.student.__init__ import student_bp
from blueprints.book.__init__ import book_bp
from database import db_session
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from models import User
import os


UPLOAD_FOLDER = '/path/files'

app = Flask(__name__)

app.register_blueprint(admin_bp,url_prefix="/admin")
app.register_blueprint(student_bp,url_prefix="/student")
app.register_blueprint(book_bp,url_prefix="/book")

app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(16)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["REMEMBER_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = True
app.config["REMEMBER_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = 'Lax'

csrf = CSRFProtect(app)
UsersStatus = []

app.jinja_env.autoescape = True | False


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "admin_bp.sign_in_page"
login_manager.login_message = "Please sign in to access this page"
login_manager.login_message_category = "info"
login_manager.session_protection = "strong"


@app.route("/")
def welcome_page():
    return redirect(url_for("student_bp.search_student"))


@app.errorhandler(404)
def error_404(error):
    return render_template("404.html")


@app.errorhandler(405)
def error_405(error):
    return render_template("404.html")


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == user_id).first()


if __name__ == "__main__":
    app.run()