from flask import Blueprint, render_template, redirect, url_for, request
from database import db_session
from models import Grade, Student


student_bp = Blueprint("student_bp",__name__,template_folder="templates")


@student_bp.route("/landing_page/")
def landing_page():
    grades = Grade.query.all()
    students = Student.query.all()
    return render_template("student/landing_page.html", grades=grades, students=students)


@student_bp.route("/landing_page/<grade>/")
def landing_page_grade(grade):
    grades = Grade.query.all()
    cer_grade = Grade.query.filter(Grade.name == grade).first()
    print(cer_grade)
    return render_template("student/landing_page.html", grades=grades, students=cer_grade.students)


@student_bp.route("/new_student",methods=["POST"])
def new_student():
    name = request.form["student_name"]
    s_grade = request.form["grade"]
    grade = Grade.query.filter(Grade.name == s_grade).first()
    n_student = Student(name,grade)
    db_session.add(n_student)
    db_session.commit()
    return redirect(url_for("student_bp.landing_page"))
