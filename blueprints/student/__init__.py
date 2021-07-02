from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file
from database import db_session
from models import Grade, Student, Book
import pandas as pd
from werkzeug.utils import secure_filename
import os
import openpyxl


student_bp = Blueprint("student_bp",__name__,template_folder="templates")

ALLOWED_EXTENSIONS = {'xlsx','xlsm','xltx','xltm'}
UPLOAD_FOLDER = '/path/files'


@student_bp.route("/all/")
def landing_page():
    grades = Grade.query.all()
    students = Student.query.all()
    return render_template("student/landing_page.html", grades=grades, students=students)


@student_bp.route("/grade/<grade>/")
def landing_page_grade(grade):
    grades = Grade.query.all()
    cer_grade = Grade.query.filter(Grade.name == grade).first()
    return render_template("student/landing_page.html", grades=grades, students=cer_grade.students)


@student_bp.route("/new_student/",methods=["POST"])
def new_student():
    name = request.form["student_name"]
    code = request.form["student_code"]
    s_grade = request.form["grade"]
    grade = Grade.query.filter(Grade.name == s_grade).first()
    n_student = Student(name,grade,int(code))
    db_session.add(n_student)
    db_session.commit()
    flash("New user successfully added", "success")
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

    flash("All students were moved up in a grade", "success")
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

    flash("All students were moved down in a grade", "success")
    return redirect(url_for("student_bp.landing_page"))


@student_bp.route("/view/<int:student_id>/")
def view_student(student_id):

    student = Student.query.filter(Student.id == student_id).first()
    grades = Grade.query.all()

    return render_template("student/student_page.html",student=student, grades=grades)


@student_bp.route("/change_grade/for/<int:student_id>/",methods=["POST"])
def change_grade(student_id):

    new_grade = Grade.query.filter(Grade.name == request.form["grade"]).first()
    student = Student.query.filter(Student.id == student_id).first()

    student.grade = new_grade
    db_session.commit()
    flash("Grade changed successfully", "success")
    return redirect(url_for("student_bp.view_student",student_id=student_id))


@student_bp.route("/<int:student_id>/rent_book/",methods=["POST"])
def rent_book(student_id):

    book = Book.query.filter(Book.code == int(request.form["code"])).first()
    if book:
        if book.student:
            flash("Book with this code is already in use","danger")
        else:
            student = Student.query.filter(Student.id == student_id).first()
            student.books.append(book)
            db_session.commit()
            flash("Book rented successfully", "success")
    else:
        flash("No book with this code !","danger")
    return redirect(url_for("student_bp.view_student",student_id=student_id))


@student_bp.route("/<int:student_id>/return_book/<int:book_id>/")
def return_book(student_id,book_id):

    book = Book.query.filter(Book.id == book_id).first()
    student = Student.query.filter(Student.id == student_id).first()

    student.books.remove(book)
    db_session.commit()
    flash("Book returned successfully","success")

    return redirect(url_for("student_bp.view_student",student_id=student_id))


@student_bp.route("/<int:student_id>/return_all/")
def return_all(student_id):

    student = Student.query.filter(Student.id == student_id).first()

    student.books.clear()
    db_session.commit()
    flash("All books returned successfully","success")

    return redirect(url_for("student_bp.view_student",student_id=student_id))


@student_bp.route("/delete/<int:student_id>/")
def delete_student(student_id):
    student = Student.query.filter(Student.id == student_id).first()
    db_session.delete(student)
    db_session.commit()
    flash("Student deleted successfully","success")
    return redirect(url_for("student_bp.landing_page"))


@student_bp.route("/search_student/")
def search_student():
    return render_template("student/search_student.html")


@student_bp.route("/search_student/",methods=["POST"])
def search_student2():
    student_code = request.form["student_code"]
    student = Student.query.filter(Student.code == student_code).first()
    if student:
        return redirect(url_for("student_bp.view_student",student_id=student.id))

    flash("No student with this code !","danger")
    return render_template("student/search_student.html")


@student_bp.route("add/multiple/<int:count>/",methods=["POST"])
def add_mul_student(count):
    grade = Grade.query.filter(Grade.name == request.form["grade"]).first()

    for i in range(count):
        name = request.form["student" + str(i)]
        code = request.form["student_code" + str(i)]

        s = Student(name,grade,code)
        db_session.add(s)
        db_session.commit()

    flash(str(count) + " students added successfully", "success")
    return redirect(url_for("student_bp.landing_page"))


@student_bp.route("read/from/excel_chart/")
def read_from_excel():
    df = pd.read_excel("static/files/students_chart.xlsx",usecols=[0,1,2,3,4])
    print(df)
    return redirect(url_for("student_bp.landing_page"))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@student_bp.route('/upload/source/excel/',methods=["POST"])
def upload_file():

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        wb_obj = openpyxl.load_workbook(file)
        sheet_obj = wb_obj.active

        for i in range(1,sheet_obj.max_row):
            name = sheet_obj.cell(row=i+1, column=2).value
            code = sheet_obj.cell(row=i+1, column=3).value
            grade_name = sheet_obj.cell(row=i+1, column=4).value
            grade = Grade.query.filter(Grade.name == grade_name).first()

            s = Student(name,grade,code)
            db_session.add(s)
            db_session.commit()

        flash("Students from chart successfully added","success")
        return redirect(url_for("student_bp.landing_page"))

    flash("Something went wrong, contact support","danger")
    return redirect(url_for("student_bp.landing_page"))

