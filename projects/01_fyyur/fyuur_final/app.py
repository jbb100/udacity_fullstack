#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import datetime
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(50))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(1000))

    shows = db.relationship('Show', backref='Venue', lazy=True)


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(1000))

    shows = db.relationship('Show', backref='Artist', lazy=True)


# Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.Date)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  result = Venue.query.outerjoin(Show, Show.venue_id == Venue.id).all()

  print('result = ', result)

  # create group id for grouping (city, sate)
  group_dict = {}

  for row in result:
    group_id = f"{row.city}^{row.state}"
    venue_id = row.id
    if group_id not in group_dict:
      # init. group_dict
      group_dict[group_id] = []

      # filtering upcoming shows
      upcoming_shows = [x for x in row.shows if x.start_time > datetime.date.today()]

      # append not duplicated venue
      group_dict[group_id].append({
        'id': row.id,
        'name': row.name,
        'num_upcoming_shows': len(upcoming_shows)
      })

  data = []
  for group_id in group_dict:
    group_id_split = group_id.split('^')
    city = group_id_split[0]
    state = group_id_split[1]
    venues = group_dict[group_id]

    data.append({
      "city": city,
      "state": state,
      "venues": venues})

  print(data)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  keyword = request.form['search_term']
  result = Venue.query.filter(Venue.name.ilike(f"%{keyword}%")).all()

  response = {
    "count": len(result),
    "data": result
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # replace with real venue data from the venues table, using venue_id
  result = Venue.query.filter(Venue.id == venue_id) \
            .outerjoin(Show, Show.venue_id == Venue.id) \
            .outerjoin(Artist, Show.artist_id == Artist.id) \
            .all()

  data = []
  for row in result:
    past_shows = []
    upcoming_shows = []
    for show in row.shows:
      artist_id = show.artist_id
      artist_name = show.Artist.name
      artist_image_link = show.Artist.image_link
      start_time = show.start_time

      show_detail = {
        "artist_id": artist_id,
        "artist_name": artist_name,
        "artist_image_link": artist_image_link,
        "start_time": str(start_time)
      }

      if start_time > datetime.date.today():
        upcoming_shows.append(show_detail)
      else:
        past_shows.append(show_detail)

    sub_data = {
      "id": row.id,
      "name": row.name,
      "genres": row.genres[1:-1].split(','),
      "address": row.address,
      "city": row.city,
      "state": row.state,
      "phone": row.phone,
      "website": row.website,
      "facebook_link": row.facebook_link,
      "seeking_talent": row.seeking_talent,
      "seekign_description": row.seeking_description,
      "image_link": row.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows)
    }
    data.append(sub_data)

  if len(data) > 0:
    data = data[0]
    print(data)
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # insert form data as a new Venue record in the db, instead
  # modify data to be the data object returned from db insertion
  error = False
  try:
    print(request.form)
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    genres = request.form.getlist('genres')
    website = request.form['website']
    seeking_talent = bool(request.form['seeking_talent'])
    seeking_description = request.form['seeking_description']

    venue = Venue(name=name, 
                  city=city, 
                  state=state, 
                  address=address, 
                  phone=phone,
                  image_link=image_link,
                  facebook_link=facebook_link,
                  genres=genres,
                  website=website,
                  seeking_talent=seeking_talent,
                  seeking_description=seeking_description)

    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred.')
    abort (400)
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # replace with real data returned from querying the database
  result = Artist.query.all()
  data = [{"id": x.id, "name": x.name} for x in result]
  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  keyword = request.form['search_term']
  result = Artist.query.filter(Artist.name.ilike(f"%{keyword}%")).all()

  response = {
    "count": len(result),
    "data": result
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # replace with real venue data from the venues table, using venue_id
  result = Artist.query.filter(Artist.id == artist_id) \
            .outerjoin(Show, Show.artist_id == Artist.id) \
            .outerjoin(Venue, Show.venue_id == Venue.id) \
            .all()

  data = []
  for row in result:
    past_shows = []
    upcoming_shows = []
    for show in row.shows:
      venue_id = show.venue_id
      venue_name = show.Venue.name
      venue_image_link = show.Venue.image_link
      start_time = show.start_time

      show_detail = {
        "venue_id": venue_id,
        "venue_name": venue_name,
        "venue_image_link": venue_image_link,
        "start_time": str(start_time)
      }

      if start_time > datetime.date.today():
        upcoming_shows.append(show_detail)
      else:
        past_shows.append(show_detail)

    sub_data = {
      "id": row.id,
      "name": row.name,
      "genres": row.genres[1:-1].split(','),
      "city": row.city,
      "state": row.state,
      "phone": row.phone,
      "website": row.website,
      "facebook_link": row.facebook_link,
      "seeking_venue": row.seeking_venue,
      "seekign_description": row.seeking_description,
      "image_link": row.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows)
    }
    data.append(sub_data)

  if len(data) > 0:
    data = data[0]
    print(data)
  
  return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_obj = Artist.query.get(artist_id)
  artist={
    "id": artist_obj.id,
    "name": artist_obj.name,
    "genres": artist_obj.genre[1:-1].split(','),
    "city": artist_obj.city,
    "state": artist_obj.state,
    "phone": artist_obj.phone,
    "website": artist_obj.website,
    "facebook_link": artist_obj.facebook_link,
    "seeking_venue": artist_obj.seeking_venue,
    "seeking_description": artist_obj.seeking_description,
    "image_link": artist_obj.image_link
  }
  # populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    print('completed', completed)
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.genres = request.form['genres']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.website = request.form['website']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_venue = request.form['seeking_venue']
    artist.seeking_description = request.form['seeking_description']
    artist.image_link = request.form['image_link']
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_obj = Artist.query.get(artist_id)
  venue={
    "id": venue_obj.id,
    "name": venue_obj.name,
    "genres": venue_obj[1:-1].split(','),
    "address": venue_obj.address,
    "city": venue_obj.city,
    "state": venue_obj.state,
    "phone": venue_obj.phone,
    "website": venue_obj.website,
    "facebook_link": venue_obj.facebook_link,
    "seeking_talent": venue_obj.seeking_talent,
    "seeking_description": venue_obj.seeking_description,
    "image_link": venue_obj.image_link
  }
  # populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    print('completed', completed)
    venue = Venue.query.get(artist_id)
    venue.name = request.form['name']
    venue.genres = request.form['genres']
    venue.address = request.form['address']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.website = request.form['website']
    venue.facebook_link = request.form['facebook_link']
    venue.seeking_talent = request.form['seeking_talent']
    venue.seeking_description = request.form['seeking_description']
    venue.image_link = request.form['image_link']
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # insert form data as a new Venue record in the db, instead
  # modify data to be the data object returned from db insertion
  error = False
  try:
    print(request.form)
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    genres = request.form.getlist('genres')
    website = request.form['website']
    seeking_venue = bool(request.form['seeking_venue'])
    seeking_description = request.form['seeking_description']

    # print(genres)

    artist = Artist(name=name, 
                  city=city, 
                  state=state, 
                  phone=phone,
                  image_link=image_link,
                  facebook_link=facebook_link,
                  genres=genres,
                  website=website,
                  seeking_venue=seeking_venue,
                  seeking_description=seeking_description)

    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred.')
    abort (400)
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  result = Show.query \
            .join(Venue, Show.venue_id == Venue.id) \
            .join(Artist, Show.artist_id == Artist.id) \
            .all()

  data = []
  for row in result:
    sub_data = {
      "venue_id": row.venue_id,
      "venue_name": row.Venue.name,
      "artist_id": row.artist_id,
      "artist_name": row.Artist.name,
      "artist_image_link": row.Artist.image_link,
      "start_time": str(row.start_time)
    }
    data.append(sub_data)

  return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # insert form data as a new Show record in the db, instead
  error = False
  try:
    print(request.form)
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    # print(genres)

    show = Show(artist_id=artist_id, 
                  venue_id=venue_id, 
                  start_time=start_time)

    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred.')
    abort (400)
  else:
    # on successful db insert, flash success
    flash('Show was successfully listed!')
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
