from flask import Blueprint, render_template


student_bp = Blueprint("student_bp",__name__,template_folder="templates")


@student_bp.route("/landing_page/")
def landing_page():
    return render_template("student/landing_page.html")
