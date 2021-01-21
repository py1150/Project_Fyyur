
# to dos
# past - upcoming shows
#   - divide by date (Shows model)
#   - on venue and artist page show past and upcoming shows; aggregate number; use model Show  
#
# new/edit venue, new/edit artist: currently seeking and edit possible for all fields which are in new / website 
# check all fields such as upcoming shows etc
# past performance / upcoming shows - count

# @app.route('/venues/<int:venue_id>')
# upcoming shows --> artist

# edit model - upcoming shows - delete migrations
# seeking veneu and artist - should be availabe in edit
# check in form if other restrictions are necessary

#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
Flask,
render_template,
request,
Response,
flash,
redirect,
url_for,
abort,
jsonify
)
from models import app, db, Venue, Artist, Show
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys

from flask_migrate import Migrate
from datetime import datetime
import re
import os
import pdb
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

#
#app.config.from_object(Config)
app.config.from_object('config')
moment = Moment(app)
db.init_app(app)
#



#app = Flask(__name__)
#moment = Moment(app)
#app.config.from_object('config')
#db = SQLAlchemy(app)

#migrate = Migrate(app, db)

# TODO: connect to a local postgresql database





#----------------------------------------------------------------------------#
# Utility Functions
#----------------------------------------------------------------------------#


# extract attribute names of data
def extract_attribute_names(data):
  data_attr = [attribute for attribute in dir(data)\
                  if (attribute[0:1] not in ['_']\
                       and attribute not in\
                       ['query','query_class','metadata'])]
  return data_attr

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

  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = Venue.query.all()
  return render_template('pages/venues.html', areas=data);

""" orig
@app.route('/venues')
def venues():

  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]
  return render_template('pages/venues.html', areas=data);
"""

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  # initialize response (dict)
  response = {}

  # query for name in db
  search_term = request.form['search_term']
  # add '%' characters to search term
  search_formatted=f'%{search_term}%'
  # query from db - case insensitive 'ilike'
  query_results = Venue.query.filter(Venue.name.ilike(search_formatted))\
                       .all()

  # store number of results found                     
  response['count'] = len(query_results) 

  # store of each result
  response['data']=[]
  for venue in query_results:
    result_dict = {}
    result_dict['id'] = venue.id
    result_dict['name'] = venue.name
    #result_dict['num_upcoming_shows'] = venue.upcoming_shows_count #2021/01/21
    response['data'].append(result_dict)
  
  #Venue.query.filter_by(name=venue_id)
  #return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

"""
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
"""


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  query = Venue.query.filter(Venue.id==venue_id)
  #data = query.all()
  data = query.first()

  #get value for genres
  # 1. clean string from special characters
  clean_str = re.sub(r'[\{}"]','',data.genres)
  genres = re.split(",",clean_str)
  
  data_attr = extract_attribute_names(data)

  # save genres and all other variables in dictionary
  # values from database + formatted genre data
  # assign empty string instead of None
  venue_dict={}
  for name in data_attr:
   
    if name=='genres':
      venue_dict[name] = genres
    else:
      venue_dict[name] = data.__getattribute__(name)
    
    if venue_dict[name]==None:
      venue_dict[name]=''
  
  
  # add show data
  #---------------
  now = datetime.now()

  # past shows
  query_past_shows = db.session\
                       .query(Venue, Show, Artist)\
                       .join(Show, Venue.id == Show.venue_id)\
                       .join(Artist, Show.artist_id == Artist.id)\
                       .filter(Venue.id==venue_id)\
                       .filter(Show.start_time<now)\
                       .all()
  
  # create past shows list
  past_shows = []
  # add a dictionary for each search result to the list
  for venue, show, artist in query_past_shows:
    past_shows_dict={}
    past_shows_dict['artist_image_link'] = artist.image_link
    past_shows_dict['artist_id'] = artist.id
    past_shows_dict['artist_name'] = artist.name
    str_time = show.start_time.strftime('%Y-%m-%d, %H:%M:%S')
    past_shows_dict['start_time'] = format_datetime(value=str_time,format='full')
    # append to list
    past_shows.append(past_shows_dict)
 
  # upcoming shows
  """
  query_upcoming_shows = Show.query.filter_by(venue_id=venue_id)\
                          .filter(Show.start_time>=datetime.now())\
                          .all()
  """
  query_upcoming_shows = db.session\
                          .query(Venue, Show, Artist)\
                          .join(Show, Venue.id == Show.venue_id)\
                          .join(Artist, Show.artist_id == Artist.id)\
                          .filter(Venue.id == venue_id)\
                          .filter(Show.start_time >= now)\
                          .all()
  
  # create past shows list
  upcoming_shows = []
  # add a dictionary for each search result to the list
  for venue, show, artist in query_upcoming_shows:
    upcoming_shows_dict={}
    upcoming_shows_dict['artist_image_link'] = artist.image_link
    upcoming_shows_dict['artist_id'] = artist.id
    upcoming_shows_dict['artist_name'] = artist.name
    str_time = show.start_time.strftime('%Y-%m-%d, %H:%M:%S')
    upcoming_shows_dict['start_time'] = format_datetime(value=str_time,format='full')
    # append to list
    upcoming_shows.append(upcoming_shows_dict)                        


  # create output
  venue_dict['past_shows_count'] = len(query_past_shows)
  venue_dict['past_shows'] = past_shows
  venue_dict['upcoming_shows_count'] = len(query_upcoming_shows)
  venue_dict['upcoming_shows'] = upcoming_shows

  #return render_template('pages/show_venue.html', venue=data)
  return render_template('pages/show_venue.html', venue=venue_dict)



"""
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }
  data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)
"""


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  error=False
  try:
    # id is the last id from table in db +1
    id_val = Venue.query.order_by(Venue.id.desc()).first().id+1 #2021/01/18
    # all other values are retrieved from the form
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    facebook_link = request.form['facebook_link']
    genres = request.form.getlist('genres') #werkzeug multidict; non-unique keys are possible: method 'getlist' to get all values
    if len(request.form['seeking_description'])>0:
      #seeking_performance = True #2021/01/18
      seeking_talent = True
    else:
      #seeking_performance = False #2021/01/18
      seeking_talent = False
    seeking_description=request.form['seeking_description']
    """ 2021/01/18
    venue = Venue(id=id_val, name=name, city=city, state=state,\
              address=address, phone=phone, facebook_link=facebook_link,\
              genres=genres, seeking_performance=seeking_performance,\
              seeking_description=seeking_description)
    """
    venue = Venue(id=id_val, name=name, city=city, state=state,\
              address=address, phone=phone, facebook_link=facebook_link,\
              genres=genres, seeking_talent=seeking_talent,\
              seeking_description=seeking_description)

    #pdb.set_trace()
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    error=True
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  if error:
    abort(400)
  else:
    return render_template('pages/home.html')

"""
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')
"""


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error=False
  try:
    venue_name = Venue.query.filter_by(id=venue_id).first().name
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue ' + venue_name + ' was successfully deleted!')
  except:
    db.session.rollback()
    flash('Venue ' + venue_name + ' was not deleted')
  finally:
    db.session.close()
  print('check error')
  print(error)
  if error:
    print("error detected")
    abort(400)
  else:
    #return render_template('pages/home.html')
    return redirect(url_for('index'))


"""
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None
"""

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  # query from database
  query_result = Artist.query.all()

  data=[]
  for result in query_result:
    result_dict={}
    result_dict['id'] = result.id
    result_dict['name'] = result.name
    # upcoming shows - extract from shows
    data.append(result_dict)

  return render_template('pages/artists.html', artists=data)

"""
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]
  return render_template('pages/artists.html', artists=data)
"""


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  # initialize response (dict)
  response = {}

  # query for name in db
  search_term = request.form['search_term']
  # add '%' characters to search term
  search_formatted=f'%{search_term}%'
  # query from db - case insensitive 'ilike'
  query_results = Artist.query.filter(Artist.name.ilike(search_formatted))\
                       .all()

  # store number of results found                     
  response['count'] = len(query_results) 

  # store of each result
  response['data']=[]
  for artist in query_results:
    result_dict = {}
    result_dict['id'] = artist.id
    result_dict['name'] = artist.name
    response['data'].append(result_dict)
  
  #return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

  

"""
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
"""

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  # query data base
  query = Artist.query.filter(Artist.id==artist_id)
  data = query.first()

  #get value for genres
  # 1. clean string from special characters
  clean_str = re.sub(r'[\{}"]','',data.genres)
  genres = re.split(",",clean_str)
  
  data_attr = extract_attribute_names(data)

  # save genres and all other variables in dictionary
  # values from database + formatted genre data
  # assign empty string instead of None
  artist_dict={}
  for name in data_attr:
   
    if name=='genres':
      artist_dict[name] = genres
    else:
      artist_dict[name] = data.__getattribute__(name)
    
    if artist_dict[name]==None:
      artist_dict[name]=''


  # add show data
  #---------------
  now = datetime.now()

  # past shows
  query_past_shows = db.session\
                       .query(Artist, Show, Venue)\
                       .join(Show, Artist.id == Show.artist_id)\
                       .join(Venue, Show.venue_id == Venue.id)\
                       .filter(Artist.id==artist_id)\
                       .filter(Show.start_time<now)\
                       .all()
  
  # create past shows list
  past_shows = []
  # add a dictionary for each search result to the list
  for arist, show, venue in query_past_shows:
    past_shows_dict={}
    past_shows_dict['venue_image_link'] = venue.image_link
    past_shows_dict['venue_id'] = venue.id
    past_shows_dict['venue_name'] = venue.name
    str_time = show.start_time.strftime('%Y-%m-%d, %H:%M:%S')
    past_shows_dict['start_time'] = format_datetime(value=str_time,format='full')
    # append to list
    past_shows.append(past_shows_dict)
 
  # upcoming shows
  query_upcoming_shows = db.session\
                           .query(Artist, Show, Venue)\
                           .join(Show, Artist.id == Show.artist_id)\
                           .join(Venue, Show.venue_id == Venue.id)\
                           .filter(Artist.id==artist_id)\
                           .filter(Show.start_time >= now)\
                           .all()
  
  # create past shows list
  upcoming_shows = []
  # add a dictionary for each search result to the list
  for artist, show, venue in query_upcoming_shows:
    upcoming_shows_dict={}
    upcoming_shows_dict['venue_image_link'] = venue.image_link
    upcoming_shows_dict['venue_id'] = venue.id
    upcoming_shows_dict['venue_name'] = venue.name
    str_time = show.start_time.strftime('%Y-%m-%d, %H:%M:%S')
    upcoming_shows_dict['start_time'] = format_datetime(value=str_time,format='full')
    # append to list
    upcoming_shows.append(upcoming_shows_dict)                        

  # create output
  artist_dict['past_shows_count'] = len(query_past_shows)
  artist_dict['past_shows'] = past_shows
  artist_dict['upcoming_shows_count'] = len(query_upcoming_shows)
  artist_dict['upcoming_shows'] = upcoming_shows
  
  #return render_template('pages/show_artist.html', artist=data)
  return render_template('pages/show_artist.html', artist=artist_dict)


"""
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }
  data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)
"""

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  # query db for current id
  query = Artist.query.filter_by(id=artist_id).first()

  # create venue dictionary
  artist = {}
  artist['id'] = query.id
  artist['name'] = query.name

  # prefill form
  form.name.data = query.name
  form.city.data = query.city
  form.state.data = query.state
  form.phone.data = query.phone
  clean_str = re.sub(r'[\{}"]','',query.genres)
  form.genres.data = re.split(",",clean_str)
  form.website.data = query.website
  form.facebook_link.data = query.facebook_link
  form.image_link.data = query.image_link
  form.seeking_description.data = query.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  #retrieve data from form
  form_data = {}
  form_data['name'] = request.form['name']
  form_data['city'] = request.form['city']
  form_data['state'] = request.form['state']
  form_data['phone'] = request.form['phone']
  form_data['genres'] = '{'+','.join([str(elem) for elem in request.form.getlist('genres')])+'}'
  form_data['website'] = request.form['website']
  form_data['facebook_link'] = request.form['facebook_link']
  form_data['image_link'] = request.form['image_link']

  # query db for current id
  query = Artist.query.filter_by(id=artist_id).first()
  
  # reduce update dictionary to changed values only
  update_dict = {key:value for (key,value) in form_data.items()\
    if value!= query.__getattribute__(key)}
  # update
  error=False
  try:
    Artist.query.filter_by(id=artist_id).update(update_dict)
    db.session.commit()
    flash('Artist ' + query.name + ' was successfully updated!')
  except:
    error=True
    db.session.rollback()
    flash('Artist ' + query.name + ' could not be updated.')
  finally:
    db.session.close()
  if error:
    abort(400)

  return redirect(url_for('show_artist', artist_id=artist_id))

"""
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))
"""


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  # query db for current id
  query = Venue.query.filter_by(id=venue_id).first()

  # create venue dictionary
  venue = {}
  venue['id'] = query.id
  venue['name'] = query.name

  # prefill form
  form.name.data = query.name
  form.city.data = query.city
  form.state.data = query.state
  form.address.data = query.address
  form.phone.data = query.phone
  clean_str = re.sub(r'[\{}"]','',query.genres)
  #venue['genres'] = re.split(",",clean_str)
  form.genres.data = re.split(",",clean_str)
  form.website.data = query.website
  form.facebook_link.data = query.facebook_link
  form.image_link.data = query.image_link
  form.seeking_description.data = query.seeking_description

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  #retrieve data from form
  form_data = {}
  form_data['name'] = request.form['name']
  form_data['city'] = request.form['city']
  form_data['state'] = request.form['state']
  form_data['address'] = request.form['address']
  form_data['phone'] = request.form['phone']
  form_data['genres'] = '{'+','.join([str(elem) for elem in request.form.getlist('genres')])+'}'
  form_data['website'] = request.form['website']
  form_data['facebook_link'] = request.form['facebook_link']
  form_data['image_link'] = request.form['image_link']

  # query db for current id
  query = Venue.query.filter_by(id=venue_id).first()
  
  # reduce update dictionary to changed values only
  update_dict = {key:value for (key,value) in form_data.items()\
    if value!= query.__getattribute__(key)}
  # update
  error=False
  try:
    Venue.query.filter_by(id=venue_id).update(update_dict)
    db.session.commit()
    flash('Venue ' + query.name + ' was successfully updated!')
  except:
    error=True
    db.session.rollback()
    flash('Venue ' + query.name + ' could not be updated.')
  finally:
    db.session.close()
  if error:
    abort(400)
  return redirect(url_for('show_venue', venue_id=venue_id))



"""
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))
"""



#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  #return render_template('pages/home.html')

  error=False
  try:
    # id is the last id from table in db +1
    try:
      id_val = Artist.query.order_by(Artist.id.desc()).first().id+1
    except:
      id_val = 1
    # all other values are retrieved from the form
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    website = request.form['website']
    facebook_link = request.form['facebook_link']
    genres = request.form.getlist('genres') #werkzeug multidict; non-unique keys are possible: method 'getlist' to get all values
    if len(request.form['seeking_description'])>0:
      seeking_performance = True
    else:
      seeking_performance = False
    seeking_description=request.form['seeking_description']
    artist = Artist(id=id_val, name=name, city=city, state=state,\
              phone=phone, website=website,\
              facebook_link=facebook_link, genres=genres,\
              seeking_performance=seeking_performance, seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    error=True
    db.session.rollback()
    flash('Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  if error:
    abort(400)
  else:
    return render_template('pages/home.html')

"""
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')
"""

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  # query db
  query = Show.query.all()

  data = []
  for show in query:
    query_venue =  Venue.query.filter_by(id=show.venue_id).first()
    query_artist = Artist.query.filter_by(id=show.artist_id).first()

    data_dict={}
    data_dict['id'] = show.id
    str_time = show.start_time.strftime('%Y-%m-%d, %H:%M:%S')
    data_dict['start_time'] = format_datetime(value=str_time,format='full')
    #data_dict['start_time'] = format_datetime(value=show.start_time,format='full')
    data_dict['venue_id'] = show.venue_id
    data_dict['venue_name'] = query_venue.name
    data_dict['artist_id'] = show.artist_id
    data_dict['artist_name'] = query_artist.name
    data_dict['artist_image_link'] = query_artist.image_link
    data.append(data_dict)

  return render_template('pages/shows.html', shows=data)

"""
@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=data)
"""

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error=False
  try:
    # id is the last id from table in db +1
    try:
      id_val = Show.query.order_by(Show.id.desc()).first().id+1
    except:
      id_val = 1
    # all other values are retrieved from the form
    #start_time = datetime.strptime(request.form['start_time'],'%Y-%m-%d %H:%M:%S')
    start_time = request.form['start_time']
    artist_id = int(request.form['artist_id'])
    venue_id = int(request.form['venue_id'])
    show = Show(id=id_val, start_time=start_time,\
      artist_id=artist_id, venue_id=venue_id)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    error=True
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  if error:
    abort(400)
  else:
  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


"""
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')
"""

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
#if __name__ == '__main__':
#    app.run()

# Or specify port manually:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
