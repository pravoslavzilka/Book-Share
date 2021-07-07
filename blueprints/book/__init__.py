from flask import Blueprint, render_template, redirect, url_for, request, flash
from database import db_session
from models import Grade, Student, Book, BookType


book_bp = Blueprint("book_bp",__name__,template_folder="templates")


@book_bp.route("/all/")
def landing_page():
    books = Book.query.all()
    free_books = Book.query.filter(Book.student == None).count()
    rent_books = Book.query.filter(Book.student).count()
    total_books = Book.query.count()

    book_types = BookType.query.all()

    return render_template("book/landing_page.html",books=books,book_types=book_types,
                           ctbooks=total_books,cfbooks=free_books,crbooks=rent_books
                           )


@book_bp.route("/type/<bt_name>/")
def book_type_page(bt_name):
    book_type = BookType.query.filter(BookType.name == bt_name).first()

    free_books = Book.query.filter(Book.student == None, Book.book_type == book_type).count()
    rent_books = Book.query.filter(Book.student, Book.book_type == book_type).count()
    total_books = Book.query.filter(Book.book_type == book_type).count()

    return render_template("book/book_type_page.html",book_type=book_type,
                           ctbooks=total_books, cfbooks=free_books, crbooks=rent_books
                           )


@book_bp.route("/total_list/")
def list_of_books():
    books = Book.query.all()
    book_types = BookType.query.all()
    return render_template("book/book_list.html", books=books,book_types=book_types)


@book_bp.route("/list/<book_state>/")
def books_state(book_state):
    book_types = BookType.query.all()
    if book_state == "free":
        books = Book.query.filter(Book.student_id == None).all()
    else:
        books = Book.query.filter(Book.student_id != None).all()

    return render_template("book/book_list.html",books=books,book_types=book_types)


@book_bp.route("/add_new/in/<bt_name>/",methods=["POST"])
def add_book_with_type(bt_name):
    book_code = request.form["book_code"]
    book = Book.query.filter(Book.code == book_code).first()

    if book:
        flash("Učebnica s týmto kódom už existuje", "danger")
        return redirect(url_for("book_bp.book_type_page",bt_name=bt_name))

    book_type = BookType.query.filter(BookType.name == bt_name).first()
    new_book = Book(int(book_code), book_type)

    db_session.add(new_book)
    try:
        db_session.commit()
    except OverflowError:
        flash("Neplatný kód", "danger")
        return redirect(url_for("book_bp.book_type_page", bt_name=bt_name))

    flash(f"Učebnica s kódom {book_code} úspešne pridaná","success")
    return redirect(url_for("book_bp.book_type_page", bt_name=bt_name))


@book_bp.route("/return/",methods=["GET"])
def return_book_view():
    return render_template("book/return_book.html")


@book_bp.route("/return/",methods=["POST"])
def return_book():
    code = int(request.form["book_code"])
    try:
        book = Book.query.filter(Book.code == code).first()
    except OverflowError:
        flash("Neplatný kód", "danger")
        return redirect(url_for("book_bp.return_book_view"))

    if book:
        if book.student:
            student = Student.query.filter(Student.id == book.student.id).first()
            student.books.remove(book)
            db_session.commit()
        flash(f"Kniha s kódom {book.code} bola úspešne vrátená","success")
        return redirect(url_for("book_bp.return_book_view"))

    flash("Neplatný kód","danger")
    return redirect(url_for("book_bp.return_book_view"))


@book_bp.route("/return/from/list/",methods=["POST"])
def return_book_from_list():
    code = int(request.form["book_code"])
    try:
        book = Book.query.filter(Book.code == code).first()
    except OverflowError:
        flash("Neplatný kód", "danger")
        return redirect(url_for("book_bp.list_of_books"))

    if book:
        if book.student:
            student = Student.query.filter(Student.id == book.student.id).first()
            student.books.remove(book)
            db_session.commit()
        flash(f"Učebnica s kódom {book.code} bola úspešne vrátená", "success")
        return redirect(url_for("book_bp.list_of_books"))

    flash("Neplatný kód", "danger")
    return redirect(url_for("book_bp.list_of_books"))


@book_bp.route("/return/with/type/",methods=["POST"])
def return_book_with_type():
    code = int(request.form["book_code"])
    try:
        book = Book.query.filter(Book.code == code).first()
    except OverflowError:
        flash("Neplatný kód", "danger")
        return redirect(url_for("book_bp.book_type_page"))

    if book:
        if book.student:
            student = Student.query.filter(Student.id == book.student.id).first()
            student.books.remove(book)
            db_session.commit()
        flash(f"Učebnica s kódom {book.code} bola úspešne vrátená", "success")
        return redirect(url_for("book_bp.book_type_page",bt_name=book.book_type.name))

    flash("Neplatný kód", "danger")
    return redirect(url_for("book_bp.book_type_page",bt_name=book.book_type.name))


@book_bp.route("/delete/",methods=['POST'])
def delete_book():
    book_code = int(request.form["book_code"])
    try:
        book = Book.query.filter(Book.code == book_code).first()
    except OverflowError:
        flash("Neplatný kód", "danger")
        return redirect(url_for("book_bp.list_of_books"))

    if book:
        book_type = BookType.query.filter(BookType.id == book.book_type_id).first()
        db_session.delete(book)
        db_session.commit()
        flash(f"Kniha s kódom {book.code} bola úspešne odstránená","success")
        return redirect(url_for("book_bp.book_type_page",bt_name=book_type.name))

    flash("Neplatný kód", "danger")
    return redirect(url_for("book_bp.list_of_books"))


@book_bp.route("/delete/from/list/",methods=['POST'])
def delete_book_from_list():
    book_code = int(request.form["book_code"])
    try:
        book = Book.query.filter(Book.code == book_code).first()
    except OverflowError:
        flash("Neplatný kód","danger")
        return redirect(url_for("book_bp.list_of_books"))

    db_session.delete(book)
    db_session.commit()
    flash(f"Kniha s kódom {book.code} bola úspešne odstránená","success")
    return redirect(url_for("book_bp.list_of_books"))


@book_bp.route("/add_type/",methods=["POST"])
def add_book_type():
    req_bt = request.form["book_name"]
    req_ba = request.form["book_author"]

    try:
        book_type = BookType.query.filter(BookType.name == req_bt).first()
    except OverflowError:
        flash("Neplatný kód","danger")
        return redirect(url_for("book_bp.landing_page"))

    if book_type:
        flash("Typ tejto učibnice už existuje","danger")
        return redirect(url_for("book_bp.landing_page"))

    new_bt = BookType(req_bt,req_ba)
    db_session.add(new_bt)
    try:
        db_session.commit()
    except OverflowError:
        flash("Neplatné údaje", "danger")
        return redirect(url_for("book_bp.landing_page"))

    flash(f"Nový typ učebníc {req_bt} bol úspešne pridaný", "success")
    return redirect(url_for("book_bp.landing_page"))


@book_bp.route("/delete/type/<int:type_id>/")
def delete_type(type_id):

    try:
        book_type = BookType.query.filter(BookType.id == type_id).first()
    except OverflowError:
        flash("Neplataný kód", "danger")
        return redirect(url_for("book_bp.landing_page"))

    count_of_books = 0
    if book_type:
        for index,book in enumerate(book_type.books):
            db_session.delete(book)
            count_of_books += 1

        db_session.delete(book_type)
        db_session.commit()
        flash(f"Typ učebnice {book_type.name} bol úspešne vymazaný a s ním {count_of_books} učebníc","success")
        return redirect(url_for("book_bp.landing_page"))

    flash("Neplataný kód", "danger")
    return redirect(url_for("book_bp.landing_page"))

