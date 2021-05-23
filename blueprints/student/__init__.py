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


@student_bp.route("/move_all_students_up/")
def move_all_s_up():

    grades = ["Prima", "Sekunda", "Tercia", "Kvarta", "Kvinta", "Sexta", "Septima", "Oktava",
              "1.A","2.A","3.A","4.A",
              "1.B", "2.B", "3.B","4.B"
              ]
    final_grades = ["Oktava","4.A","4.B"]
    students = Student.query.all()

    for student in students:
        if student.grade.name in final_grades:
            db_session.delete(student)
            db_session.commit()
            continue
        index = grades.index(student.grade.name)
        new_grade = Grade.query.filter(Grade.name == grades[index+1]).first()
        student.grade = new_grade
        db_session.commit()

    return redirect(url_for("student_bp.landing_page"))


@student_bp.route("/move_all_students_down/")
def move_all_s_down():

    grades = ["Prima", "Sekunda", "Tercia", "Kvarta", "Kvinta", "Sexta", "Septima", "Oktava",
              "1.A","2.A","3.A","4.A",
              "1.B", "2.B", "3.B","4.B"
              ]
    final_grades = ["Prima","1.A","1.B"]
    students = Student.query.all()

    for student in students:
        if student.grade.name in final_grades:
            db_session.delete(student)
            db_session.commit()
            continue
        index = grades.index(student.grade.name)
        new_grade = Grade.query.filter(Grade.name == grades[index-1]).first()
        student.grade = new_grade
        db_session.commit()

    return redirect(url_for("student_bp.landing_page"))
