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


@book_bp.route("/delete/<int:book_id>/")
def delete_book(book_id):
    book = Book.query.filter(Book.id == book_id).first()
    db_session.delete(book)
    db_session.commit()
    flash("Book deleted successfully","danger")
    return redirect(url_for("book_bp.landing_page"))
