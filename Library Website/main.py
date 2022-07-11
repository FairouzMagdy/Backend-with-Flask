from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'romany'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///new-books-collection.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
all_books = []


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Book {self.title}>'


db.create_all()


class BookForm(FlaskForm):
    title = StringField(label='Book Name', validators=[DataRequired()])
    author = StringField(label='Book Author', validators=[DataRequired()])
    rating = FloatField(label='Rating', validators=[DataRequired()])
    submit = SubmitField(label='Add Book')


class EditForm(FlaskForm):
    new_rating = FloatField(validators=[DataRequired()])
    submit = SubmitField(label='Change Rating')


@app.route('/')
def home():
    books = db.session.query(Book).all()
    return render_template('index.html', books=books)


@app.route("/add", methods=['POST', 'GET'])
def add():
    form = BookForm()
    new_data = form.data
    if form.validate_on_submit():
        new_book = {key: value for (key, value) in new_data.items() if key not in ['submit', 'csrf_token']}
        all_books.append(new_book)
        new_book = Book(title=form.title.data, author=form.author.data, rating=form.rating.data)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add.html', form=form)


@app.route('/edit/<int:id>', methods=['POST', 'GET'])
def edit(id):
    edit_form = EditForm()
    book_to_update = Book.query.get(id)
    if edit_form.validate_on_submit():
        # update
        book_to_update.rating = edit_form.new_rating.data
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('edit_rating.html', form=edit_form, book=book_to_update)


@app.route('/delete/<int:id>')
def delete(id):
    book_to_delete = Book.query.get(id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
