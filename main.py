from flask import *
import requests
from flask_sqlalchemy import SQLAlchemy
from secret_keys import MOVIE_DB_API_KEY

# import sqlite3


POSTER_URL_PATH = "http://image.tmdb.org/t/p/w500"
TMDB_API_PATH = f"https://api.themoviedb.org/3/search/movie?api_key={MOVIE_DB_API_KEY}&query="

# this is more error prone due to working directly with SQL commands
# db = sqlite3.connect("books-collection.db")
# cursor = db.cursor()
# # cursor.execute("CREATE TABLE books (id INTEGER PRIMARY KEY, title varchar(250) NOT NULL UNIQUE, author varchar(250) "
# #                "NOT NULL, rating FLOAT NOT NULL)")
# cursor.execute("INSERT INTO books VALUES(2, 'Harry Po2tter', 'J2. K. Rowling', '92.3')")
# db.commit()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies_db.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

all_movies = []


class movies(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    rating = db.Column(db.Float)
    image = db.Column(db.String(200))

    def __init__(self, name, rating, image):
        self.name = name
        self.rating = rating
        self.image = image


@app.route('/')
def home():
    all_movoies_db = db.session.query(movies).all()
    print(all_movoies_db)
    all_movies = []
    for movie in all_movoies_db:
        movie_dict = {
            "name": movie.name,
            "rating": str(movie.rating),
            "image": str(POSTER_URL_PATH + movie.image)
        }

        all_movies.append(movie_dict)

    return render_template("index.html", movies=all_movies)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        name = request.form.get("name")
        rating = request.form.get("rating")
        response = requests.get(TMDB_API_PATH + name).json()
        image = (response["results"][0]["poster_path"])
        movie = movies(name, rating, image)
        db.session.add(movie)
        db.session.commit()
        all_movoies_db = db.session.query(movies).all()
        for movie in all_movoies_db:
            movie_dict = {
                "name": movie.name,
                "rating": str(movie.rating),
                "image": str(POSTER_URL_PATH + movie.image)
            }

            all_movies.append(movie_dict)

    return render_template("add.html")


@app.route("/delete")
def delete():
    movie_name = request.args.get('id')
    movie_to_delete = db.session.query(movies).filter_by(name=movie_name).first()
    db.session.delete(movie_to_delete)
    db.session.commit()

    return redirect(url_for("home"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)
