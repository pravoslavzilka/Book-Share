from flask import Blueprint, render_template, redirect, url_for, request, flash
from database import db_session
from models import Grade, Student, Book, BookType


book_bp = Blueprint("book_bp",__name__,template_folder="templates")


@book_bp.route("/all/")
def landing_page():
    books = Book.query.all()
    book_types = BookType.query.all()

    return render_template("book/landing_page.html",books=books,book_types=book_types)


@book_bp.route("/<book_state>/")
def books_state(book_state):
    book_types = BookType.query.all()
    if book_state == "free":
        books = Book.query.filter(Book.student_id == None).all()
    else:
        books = Book.query.filter(Book.student_id != None).all()

    return render_template("book/landing_page.html",books=books,book_types=book_types)


@book_bp.route("/add_new/",methods=["POST"])
def add_book():
    book_code = request.form["book_code"]
    book = Book.query.filter(Book.code == book_code).first()
    if book:
        flash("Book with this code already exist","danger")
        return redirect(url_for("book_bp.landing_page"))

    book_type = BookType.query.filter(BookType.name == request.form["book_type"]).first()
    new_book = Book(int(book_code),book_type)

    db_session.add(new_book)
    db_session.commit()

    flash("New book successfully added", "success")
    return redirect(url_for("book_bp.landing_page"))


@book_bp.route("/return/",methods=["POST"])
def return_book():
    code = int(request.form["book_code"])
    book = Book.query.filter(Book.code == code).first()

    if book:
        if book.student:
            student = Student.query.filter(Student.id == book.student.id).first()
            student.books.remove(book)
            db_session.commit()
        flash("Book returned successfully","success")
        return redirect(url_for("book_bp.landing_page"))

    flash("No book with this code","danger")
    return redirect(url_for("book_bp.landing_page"))


@book_bp.route("/delete/<int:book_id>/")
def delete_book(book_id):
    book = Book.query.filter(Book.id == book_id).first()
    db_session.delete(book)
    db_session.commit()
    flash("Book deleted successfully","success")
    return redirect(url_for("book_bp.landing_page"))


@book_bp.route("/add_type/",methods=["POST"])
def add_book_type():
    req_bt = request.form["book_type"]
    book_type = BookType.query.filter(BookType.name == req_bt).first()
    if book_type:
        flash("This book type already exist","danger")
        return redirect(url_for("book_bp.landing_page"))

    new_bt = BookType(req_bt)
    db_session.add(new_bt)
    db_session.commit()

    flash("New book type successfully added", "success")
    return redirect(url_for("book_bp.landing_page"))


@book_bp.route("/generate/form/",methods=["POST"])
def generate_form():
    count = int(request.form["count"])
    sl_bt = request.form["sl_bt"]
    book_types = BookType.query.all()
    return render_template("book/book_add_form.html",count=count,sl_bt=sl_bt,book_types=book_types)


@book_bp.route("add/multiple/<int:count>/",methods=["POST"])
def add_multiple_book(count):
    book_type = BookType.query.filter(BookType.name == request.form["book_type"]).first()

    for i in range(count):
        code = request.form["book_code" + str(i)]
        b = Book(code,book_type)
        db_session.add(b)
        db_session.commit()

    flash(str(count) + " books added successfully","success")
    return redirect(url_for("book_bp.landing_page"))
