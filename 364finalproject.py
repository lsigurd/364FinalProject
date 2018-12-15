###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, RadioField, ValidationError, FileField, PasswordField, BooleanField, SelectMultipleField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Shell 
import requests
import json
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin
from flask_migrate import Migrate, MigrateCommand
from threading import Thread
from werkzeug import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

## App setup code
app = Flask(__name__)
app.debug = True
app.use_reloader = True

## All app.config values

app.config['SECRET_KEY'] = 'hard to guess string from si364'
## TODO 364: Create a database in postgresql in the code line below, and fill in your app's database URI. It should be of the format: postgresql://localhost/YOUR_DATABASE_NAME

##Postgres database is "lsigurdMidterm"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://laurensigurdson@localhost:5432/lsigurdFinal"

## Provided:
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Set up Flask debug and necessary additions to app
manager = Manager(app)
db = SQLAlchemy(app) # For database use
migrate = Migrate(app, db) # For database use/updating
manager.add_command('db', MigrateCommand) # Add migrate command to manager

# Login configurations setup
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app) # set up login manager


##################
##### MODELS #####
##################

# Special model for users to log in
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

#Creating 4 tables (Movie, Actor, Director, Genre) 

#One-to-many: Movie, Actor
#many-to-many: Genre, Director

# Set up association Table between genres and directors
collections = db.Table('collections',db.Column('genre_id',db.Integer, db.ForeignKey('genres.id')),db.Column('director_id',db.Integer, db.ForeignKey('directors.id')))


class Movie(db.Model):
    __tablename__ = "movies"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64))
    rating = db.Column(db.Integer)
    genre_id = db.Column(db.Integer, db.ForeignKey("genres.id")) 
    director_id = db.Column(db.Integer,db.ForeignKey("directors.id"))
    actors = db.relationship('Actor',backref='Movie') # building the relationship -- one movie, many actors

class Genre(db.Model):
    __tablename__ = "genres"
    id = db.Column(db.Integer, primary_key=True)
    genre_name = db.Column(db.String(64))
    movies = db.relationship('Movie',backref='Genre')
    directors = db.relationship('Director',secondary=collections,backref=db.backref('genres',lazy='dynamic'),lazy='dynamic')

class Director(db.Model):
    __tablename__ = "directors"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255))
    movies = db.relationship('Movie',backref='Director') # building the relationship -- one director, many movies


class Actor(db.Model):
    __tablename__ = "actors"
    id = db.Column(db.Integer, primary_key=True)
    actor_name = db.Column(db.String(64))
    movie_id = db.Column(db.Integer,db.ForeignKey("movies.id"))


## DB load functions
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) # returns User object or None


# Custom validation for this form so that the movie name is at least 3 characters
def validate_movie_name(self, field):
    user_input = field.data
    if len(user_input) < 3:
        raise ValidationError("Your movie name must be at least 3 characters")

def validate_genre(self, field):
    user_input = field.data
    #genres taken from IMDb Movies
    if user_input not in ["Action", "Adventure", "Animation", "Biography", "Comedy", "Crime", "Documentary", "Drama", "Family", "Fantasy", "Film Noir", "Game-Show", "History", "Horror", "Music", "Musical", "Mystery", "News", "Reality-TV", "Romance", "Sci-Fi", "Short", "Sport", "Talk Show", "Thriller", "War", "Western"]:
        raise ValidationError("That is not an option for a genre")

# def validate_search_rating(self, field):
#     user_input = field.data
#     if user_input not in [1, 2, 3, 4, 5]:
#         raise ValidationError("The searched rating must be from 1-5")

def validate_update_rating(self, field):
    user_input = field.data
    if user_input not in ['1', '2', '3', '4', '5']:
        raise ValidationError("Your updated rating must be from 1-5")

###################
###### FORMS ######
###################

#####  LOGIN/REGISTRATION FORMS #######
class RegistrationForm(FlaskForm):
    email = StringField('Email:', validators=[Required(),Length(1,64),Email()])
    username = StringField('Username:',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Usernames must have only letters, numbers, dots or underscores')])
    password = PasswordField('Password:',validators=[Required(),EqualTo('password2',message="Passwords must match")])
    password2 = PasswordField("Confirm Password:",validators=[Required()])
    submit = SubmitField('Register User')

    #Additional checking methods for the form
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

##### OTHER FORMS #######

class MovieForm(FlaskForm):
    movie_name = StringField("Please enter a movie name (must be at least 3 characters): ",validators=[Required(), validate_movie_name])
    movie_genre = StringField("Please enter the movie genre: ",validators=[Required(), validate_genre])
    movie_rating = RadioField('How much do you like this movie? (1 low, 5 high)', choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5')], validators=[Required()])
    submit = SubmitField("Submit")

class RatingForm(FlaskForm):
    rating_search = IntegerField("Please enter a rating 1-5 to see all movies with this rating: ", validators=[Required()])
    submit = SubmitField("Submit")


##### UPDATE/DELETE FORMS #######

class DeleteButtonForm(FlaskForm):
    submit = SubmitField("Delete this Actor")

class UpdateButtonForm(FlaskForm):
    submit = SubmitField("Update Rating for This Movie")

class UpdateRatingForm(FlaskForm):
    new_rating = StringField("Enter the new rating of this movie: ", validators=[Required(), validate_update_rating])
    submit = SubmitField("Update Rating of Movie")



######################################
######## HELPER FXNS (If any) ########
######################################

def get_or_create_director(director_name):
    director_one = Director.query.filter_by(full_name = director_name).first()
    if director_one:
        return director_one
    else: 
        director_two = Director(full_name = director_name)
        db.session.add(director_two)
        db.session.commit()
        print ("added director successfully")
        return director_two

def get_or_create_genre(genre_name, director):
    genre_one = Genre.query.filter_by(genre_name = genre_name).first()
    director = get_or_create_director(director)
    if genre_one:
        genre_one.directors.append(director)
        db.session.commit()
        return genre_one
    else: 
        genre_two = Genre(genre_name = genre_name)
        genre_two.directors.append(director)
        db.session.add(genre_two)
        db.session.commit()
        print ("added genre successfully")
        return genre_two

def get_or_create_movie(movie_title, director, genre, rating):
    movie_query = Movie.query.filter_by(name = movie_title).first()
    if movie_query:
        return movie_query
    else:
        director_query = Director.query.filter_by(full_name = director).first()
        genre_query = Genre.query.filter_by(genre_name = genre).first()
        movie_one = Movie(name = movie_title, director_id = director_query.id, genre_id = genre_query.id, rating = rating)
        db.session.add(movie_one)
        db.session.commit()
        print ("added movie successfully")
        return movie_one

def get_or_create_actor(actor, movie):
    actor_query = Actor.query.filter_by(actor_name = actor).first()
    if actor_query:
        return actor_query
    else: 
        movie_query = Movie.query.filter_by(name = movie).first()
        actor_one = Actor(actor_name = actor, movie_id = movie_query.id)
        db.session.add(actor_one)
        db.session.commit()
        print("added actor successfully")
        return actor_one

def delete_actor(name):
    the_actor = Actor.query.filter_by(actor_name=name).first()
    db.session.delete(the_actor)
    db.session.commit()
    flash("***Successfully Deleted: {}***".format(the_actor.actor_name))



##################
##### Routes #####
##################

## Error handling route
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
    


#######################
###### VIEW FXNS ######
#######################

###### LOGIN/REGISTER ROUTES ######

@app.route('/login',methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html',form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('index'))

@app.route('/register',methods=["GET","POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,username=form.username.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You can now log in!')
        return redirect(url_for('login'))
    return render_template('register.html',form=form)

@app.route('/secret')
@login_required
def secret():
    return "Only authenticated users can do this! Try to log in or contact the site admin."


##### OTHER ROUTES #####

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    # Initialize the form
    form = MovieForm()
    search_form = RatingForm(request.args)

    if form.validate_on_submit():
        movie_name = form.movie_name.data
        movie_genre = form.movie_genre.data
        movie_rating = form.movie_rating.data
        
        print("hiiiiiiii")
        print(movie_name)
        print(movie_genre)
        print(movie_rating)

        baseurl = 'http://www.omdbapi.com/?apikey=9bdba9be'
        params = {}
        params["t"] = movie_name
        api_request = requests.get(baseurl, params = params)
        movie_dict = json.loads(api_request.text)

        if "Error" in movie_dict:
            print("Nope not there")
            flash("Please check your spelling or enter another movie. That movie was not found in the API")
            return render_template('index.html', form = form, search_form = search_form)
        else:
            movie_director = str(movie_dict['Director'])
            actor_string = str(movie_dict['Actors'])
            actor_list = actor_string.split(",")
            
            print(movie_director)
            print(actor_list)
            
            movie_query = Movie.query.filter_by(name = movie_name).first() 

            if movie_query:
                flash("Someone already entered this movie in the database")
                return render_template('index.html', form = form, search_form = search_form)
            else:
                query_director = get_or_create_director(movie_director)
                query_genre = get_or_create_genre(movie_genre, movie_director)
                query_movie = get_or_create_movie(movie_name, movie_director, movie_genre, movie_rating)
                for actor in actor_list:
                    query_actor = get_or_create_actor(actor, movie_name)
        
                flash("movie successfully added to the db")
                return redirect(url_for('form_result'))     

    search_results = None
    if search_form.validate():
        rating_search = int(search_form.rating_search.data)
        if rating_search not in [1,2,3,4,5]:
            flash("Rating must be from 1-5")
            return render_template('index.html', form = form, search_form = search_form)
        search_results = Movie.query.filter_by(rating = rating_search).all()
        if not search_results:
            flash("No results found for this rating")
            return render_template('index.html', form = form, search_form = search_form)
        else:
            print(search_results)


    # If the form did NOT validate / was not submitted
    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    return render_template('index.html', form = form, search_form = search_form, results = search_results) 


@app.route('/result')
def form_result():
    form = UpdateButtonForm()
    all_movies = []
    all_actors = []
    movies = Movie.query.all()
    actors = Actor.query.all()
    for m in movies:
        director = Director.query.filter_by(id = m.director_id).first()
        genre = Genre.query.filter_by(id = m.genre_id).first()
        all_movies.append((m.name, m.rating, director.full_name, genre.genre_name))
    
    for a in actors:
        movie = Movie.query.filter_by(id = a.movie_id).first()
        all_actors.append((a.actor_name, movie.name))
    
    return render_template('result.html', all_movies = all_movies, form = form, all_actors = all_actors)

@app.route('/actors', methods=["GET","POST"])
def see_all_actors():
    form = DeleteButtonForm()
    all_actors = []
    actors = Actor.query.all()
    for a in actors:
        all_actors.append(a.actor_name)
    return render_template('actors.html', all_actors = all_actors, form = form)

@app.route('/directors')
def see_all_directors():
    all_directors = []
    directors = Director.query.all()
    for d in directors:
        all_directors.append(d.full_name)
    return render_template('directors.html', all_directors = all_directors)

@app.route('/genres')
def see_all_genres():
    genres = Genre.query.all()
    all_genres = []
    for g in genres:
        ## Querying the association table and filtering using genre ID to count number of directors in any given genre.
        total_directors = db.session.query(collections).filter_by(genre_id=g.id).all()
        all_genres.append((g.genre_name, len(total_directors)))

    return render_template('genres.html', all_genres = all_genres)


#### UPDATE/DELETE ROUTES ######

@app.route('/delete/<actor>',methods=["GET","POST"])
def delete(actor):
    delete_actor(actor)
    return redirect(url_for('see_all_actors'))


@app.route('/update/<movie>',methods=["GET","POST"])
def update(movie):
    form = UpdateRatingForm()
    if form.validate_on_submit():
        new_rating = form.new_rating.data
        movie = Movie.query.filter_by(name = movie).first()
        movie.rating = new_rating
        db.session.commit()
        flash("***Updated Rating of {}***".format(movie.name))
        return redirect(url_for('form_result'))
    
    # # If the form did NOT validate / was not submitted
    if (form.new_rating.data != ''):
        errors = [v for v in form.errors.values()]
        if len(errors) > 0:
            flash("errors in submission - " + str(errors))
    return render_template('update_movie.html', movie=movie, form=form)


## Code to run the application...

# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!

if __name__ == '__main__':
    db.create_all() # Will create any defined models when you run the application
    app.run(use_reloader=True,debug=True) # The usual


































