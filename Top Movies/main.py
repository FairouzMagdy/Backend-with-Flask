from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies-collection.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MOVIE_DB_API_KEY = '38a03a06ee1a2aa73797c431bb4c2de5'
MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

Bootstrap(app)
db = SQLAlchemy(app)

movies_titles = []
movies_date = []
movies_overview = []
movies_posters = []


class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(550), unique=True, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, unique=True, nullable=True)
    review = db.Column(db.String(550), nullable=True)
    img_url = db.Column(db.String(250), unique=True, nullable=False)


db.create_all()

new_movie = Movies(
    title="Phone Booth",
    year=2002,
    description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's\
     sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a \
     jaw-dropping climax.",
    rating=7.3,
    ranking=10,
    review="My favourite character was the caller.",
    img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
)


class EditForm(FlaskForm):
    rating = FloatField(label='Your Rating Out of 10:', validators=[DataRequired()])
    review = StringField(label='Your Review', validators=[DataRequired()])
    submit = SubmitField(label='Done')


class AddForm(FlaskForm):
    movie_title = StringField(label='Movie Title', validators=[DataRequired()])
    submit = SubmitField(label='Add Movie')


# db.session.add(new_movie)
# db.session.commit()


@app.route("/")
def home():
    movies = Movies.query.order_by(Movies.rating).all()
    for i in range(len(movies)):
        movies[i].ranking = len(movies) - i
    return render_template("index.html", movies=movies)


@app.route("/edit/<int:id>", methods=['GET', 'POST'])
def edit(id):
    form = EditForm()
    updated_movie = Movies.query.get(id)
    if form.validate_on_submit():
        # update db
        updated_movie.rating = form.rating.data
        updated_movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=form, movie=updated_movie)


@app.route('/delete/<int:id>')
def delete(id):
    movie = Movies.query.get(id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/add', methods=['POST', 'GET'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        movie_title = form.movie_title.data
        response = requests.get(MOVIE_DB_SEARCH_URL, params={"api_key": MOVIE_DB_API_KEY, "query": movie_title})
        movies_data = response.json()['results']
        return render_template('select.html', movies=movies_data)
    return render_template('add.html', form=form)


@app.route('/find')
def find_movie():
    movie_api_id = request.args.get('id')
    if movie_api_id:
        movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_api_id}"
        response = requests.get(movie_api_url, params={"api_key": MOVIE_DB_API_KEY, "language": "en-US"})
        movie_data = response.json()
        movie_added = Movies(
            title=movie_data['title'],
            year=movie_data['release_date'],
            description=movie_data['overview'],
            img_url=MOVIE_DB_IMAGE_URL + movie_data['poster_path'],
        )
        db.session.add(movie_added)
        db.session.commit()
        return redirect(url_for('edit', id=movie_added.id))


if __name__ == '__main__':
    app.run(debug=True)
