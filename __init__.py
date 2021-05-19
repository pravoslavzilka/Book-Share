from flask import Flask, render_template
from blueprints.admin.__init__ import admin_bp
from database import db_session
from flask_login import LoginManager
from models import User
import os


app = Flask(__name__)

app.register_blueprint(admin_bp,url_prefix="/admin")

app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(16)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "admin_bp_.sign_in_page"
login_manager.login_message = "Please sign in to access this page"
login_manager.login_message_category = "info"


@app.route("/")
def welcome_page():
    return render_template("index.html")


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == user_id).first()


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)