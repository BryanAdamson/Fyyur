# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from forms import *
from models import *
import sys

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db.init_app(app)

migrate = Migrate(app, db)


# TODO: connect to a local postgresql database



# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    #
    venues = db.session.query(Venue.city, Venue.state).distinct().all()

    data = []

    for area in venues:

        areaVenues = Venue.query.filter_by(state=area.state, city=area.city).all()

        venue_data = []
        for venue in areaVenues:

            venue_data.append({
                "id": venue.id,
                "name": venue.name,
            })

        data.append({
            "city": area.city,
            "state": area.state,
            "venues": venue_data
        })


    # data = [{
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "venues": [{
    #         "id": 1,
    #         "name": "The Musical Hop",
    #         "num_upcoming_shows": 0,
    #     }, {
    #         "id": 3,
    #         "name": "Park Square Live Music & Coffee",
    #         "num_upcoming_shows": 1,
    #     }]
    # }, {
    #     "city": "New York",
    #     "state": "NY",
    #     "venues": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }]
    return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')
    responseData = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
    response = {}
    response['count'] = len(responseData)
    response['data'] = responseData

    # response = {
    #     "count": 1,
    #     "data": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    realData = Venue.query.get(venue_id)
    data = {}
    data['id'] = realData.id
    data['name'] = realData.name
    data['address'] = realData.address
    data['phone'] = realData.phone
    data['genres'] = realData.genres
    data['website'] = realData.website
    data['facebook_link'] = realData.facebook_link
    data['seeking_talent'] = realData.seeking_talent
    data['seeking_description'] = realData.seeking_description
    data['image_link'] = realData.image_link
    data['upcoming_shows'] = Show.query \
        .join(Artiste, Show.artiste_id == Artiste.id) \
        .add_columns(Show.venue_id,
                     Artiste.id.label('artiste_id'),
                     Artiste.name.label('artiste_name'),
                     Artiste.image_link.label('artiste_image_link'),
                     Show.start_time) \
        .filter(Show.start_time >= datetime.now(), Show.venue_id == venue_id)
    data['past_shows'] = Show.query \
        .join(Artiste, Show.artiste_id == Artiste.id) \
        .add_columns(Show.venue_id,
                     Artiste.id.label('artiste_id'),
                     Artiste.name.label('artiste_name'),
                     Artiste.image_link.label('artiste_image_link'),
                     Show.start_time) \
        .filter(Show.start_time < datetime.now(), Show.venue_id == venue_id)
    data['upcoming_shows_count'] = data['upcoming_shows'].count()
    data['past_shows_count'] = data['past_shows'].count()

    # data1 = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #     "past_shows": [{
    #         "artiste_id": 4,
    #         "artist_name": "Guns N Petals",
    #         "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #         "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data2 = {
    #     "id": 2,
    #     "name": "The Dueling Pianos Bar",
    #     "genres": ["Classical", "R&B", "Hip-Hop"],
    #     "address": "335 Delancey Street",
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "914-003-1132",
    #     "website": "https://www.theduelingpianos.com",
    #     "facebook_link": "https://www.facebook.com/theduelingpianos",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 0,
    # }
    # data3 = {
    #     "id": 3,
    #     "name": "Park Square Live Music & Coffee",
    #     "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    #     "address": "34 Whiskey Moore Ave",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "415-000-1234",
    #     "website": "https://www.parksquarelivemusicandcoffee.com",
    #     "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "past_shows": [{
    #         "artiste_id": 5,
    #         "artist_name": "Matt Quevedo",
    #         "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #         "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [{
    #         "artiste_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #         "artiste_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #         "artiste_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 1,
    # }
    # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
    return render_template('pages/show_venue.html', venue=data)


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
    error = False
    try:
        newVenue = Venue(name=request.form.to_dict()['name'],
                         city=request.form.to_dict()['city'],
                         state=request.form.to_dict()['state'],
                         address=request.form.to_dict()['address'],
                         phone=request.form.to_dict()['phone'],
                         genres=request.form.to_dict()['genres'],
                         facebook_link=request.form.to_dict()['facebook_link'],
                         image_link=request.form.to_dict()['image_link'],
                         website=request.form.to_dict()['website_link'],
                         seeking_description=request.form.to_dict()['seeking_description'])
        if newVenue.seeking_talent:
            newVenue.seeking_talent = True
        else:
            newVenue.seeking_talent = False
        db.session.add(newVenue)
        db.session.commit()
    except():
        db.session.rollback()
        error = True
        print(sys.exc_info)
    finally:
        db.session.close()
    if not error:
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        # on unsuccessful db insert, flash error.
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete')
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
        deleteVenue = Venue.query.get(venue_id)
        if not deleteVenue:
            flash('Venue does not exist!')
        else:
            db.session.delete(deleteVenue)
            db.session.commit()

    except():
        db.session.rollback()
        error = True
        print(sys.exc_info)
    finally:
        db.session.close()
    if not error:
        # on successful db delete, flash success
        flash('Venue was successfully deleted!')
    else:
        # TODO: on unsuccessful db delete, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be deleted.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        # on unsuccessful db insert, flash error.
        flash('An error occurred. Venue could not be deleted.')

        # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
        # clicking that button delete it from the db then redirect the user to the homepage

    return render_template('pages/home.html')





#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = Artiste.query.all()

    # data = [{
    #     "id": 4,
    #     "name": "Guns N Petals",
    # }, {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    # }, {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    # }]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    responseData = Artiste.query.add_columns(Artiste.id, Artiste.name).filter(
        Artiste.name.ilike('%' + search_term + '%')).all()
    response = {}
    response['count'] = len(responseData)
    response['data'] = responseData

    # response = {
    #     "count": 1,
    #     "data": [{
    #         "id": 4,
    #         "name": "Guns N Petals",
    #         "num_upcoming_shows": 0,
    #     }]
    # }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artiste_id
    # TODO: replace with real artist data from the artist table, using artiste_id
    realData = Artiste.query.get(artist_id)
    data = {}
    data['id'] = realData.id
    data['name'] = realData.name
    data['phone'] = realData.phone
    data['website'] = realData.website
    data['genres'] = realData.genres
    data['facebook_link'] = realData.facebook_link
    data['seeking_venue'] = realData.seeking_venue
    data['seeking_description'] = realData.seeking_description
    data['image_link'] = realData.image_link
    data['upcoming_shows'] = Show.query \
        .join(Venue, Show.venue_id == Venue.id) \
        .add_columns(Show.artiste_id,
                     Venue.id.label('venue_id'),
                     Venue.name.label('venue_name'),
                     Venue.image_link.label('venue_image_link'),
                     Show.start_time) \
        .filter(Show.start_time >= datetime.now(), Show.artiste_id == artist_id)
    data['past_shows'] = Show.query \
        .join(Venue, Show.venue_id == Venue.id) \
        .add_columns(Show.artiste_id,
                     Venue.id.label('venue_id'),
                     Venue.name.label('venue_name'),
                     Venue.image_link.label('venue_image_link'),
                     Show.start_time) \
        .filter(Show.start_time < datetime.now(), Show.artiste_id == artist_id)
    data['upcoming_shows_count'] = data['upcoming_shows'].count()
    data['past_shows_count'] = data['past_shows'].count()

    # data1 = {
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "past_shows": [{
    #         "venue_id": 1,
    #         "venue_name": "The Musical Hop",
    #         "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #         "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data2 = {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    #     "genres": ["Jazz"],
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "300-400-5000",
    #     "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    #     "seeking_venue": False,
    #     "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "past_shows": [{
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data3 = {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    #     "genres": ["Jazz", "Classical"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "432-325-5432",
    #     "seeking_venue": False,
    #     "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [{
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 3,
    # }
    #data = list(filter(lambda d: d['id'] == artiste_id, [data1, data2, data3]))[0]
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artiste = Artiste.query.get(artist_id)

    # artist = {
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    # }
    # TODO: populate form with fields from artist with ID <artiste_id>
    return render_template('forms/edit_artist.html', form=form, artist=artiste)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artiste_id> using the new attributes
    error = False
    try:
        artiste = Artiste.query.get(artist_id)
        artiste.name=request.form.to_dict()['name']
        artiste.city = request.form.to_dict()['city']
        artiste.state = request.form.to_dict()['state']
        artiste.phone = request.form.to_dict()['phone']
        artiste.genres = request.form.to_dict()['genres']
        artiste.facebook_link = request.form.to_dict()['facebook_link']
        artiste.image_link = request.form.to_dict()['image_link']
        artiste.website = request.form.to_dict()['website_link']
        artiste.seeking_venue = request.form.to_dict()['seeking_venue']
        artiste.seeking_description = request.form.to_dict()['seeking_description']
        if artiste.seeking_venue == 'y':
            artiste.seeking_venue = True
        else:
            artiste.seeking_venue = False
        db.session.add(artiste)
        db.session.commit()
    except():
        db.session.rollback()
        error = True
        print(sys.exc_info)
    finally:
        db.session.close()
    if not error:
        # on successful db insert, flash success
        flash('Artiste ' + request.form['name'] + ' was successfully edited')
    else:
        # on unsuccessful db insert, flash error.
        flash('An error occurred. Artiste ' + request.form['name'] + ' could not be edited.')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    # venue = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    # }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    error = False
    try:
        venue = Venue.query.get(venue_id)
        venue.name = request.form.to_dict()['name'],
        venue.city = request.form.to_dict()['city']
        venue.state = request.form.to_dict()['state']
        venue.address = request.form.to_dict()['address']
        venue.phone = request.form.to_dict()['phone']
        venue.genres = request.form.to_dict()['genres']
        venue.facebook_link = request.form.to_dict()['facebook_link']
        venue.image_link = request.form.to_dict()['image_link']
        venue.website = request.form.to_dict()['website_link']
        venue.seeking_talent = request.form.to_dict()['seeking_talent']
        venue.seeking_description = request.form.to_dict()['seeking_description']
        if venue.seeking_talent == 'y':
            venue.seeking_talent = True
        else:
            venue.seeking_talent = False
        db.session.add(venue)
        db.session.commit()
    except():
        db.session.rollback()
        error = True
        print(sys.exc_info)
    finally:
        db.session.close()
    if not error:
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    else:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be updated.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        # on unsuccessful db insert, flash error.
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')

    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artiste
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
    error = False
    try:
        newArtiste = Artiste(name=request.form.to_dict()['name'],
                             city=request.form.to_dict()['city'],
                             state=request.form.to_dict()['state'],
                             phone=request.form.to_dict()['phone'],
                             genres=request.form.to_dict()['genres'],
                             facebook_link=request.form.to_dict()['facebook_link'],
                             image_link=request.form.to_dict()['image_link'],
                             website=request.form.to_dict()['website_link'],
                             seeking_description=request.form.to_dict()['seeking_description'])
        if newArtiste.seeking_venue:
            newArtiste.seeking_venue = True
        else:
            newArtiste.seeking_venue = False
        db.session.add(newArtiste)
        db.session.commit()
    except():
        db.session.rollback()
        error = True
        print(sys.exc_info)
    finally:
        db.session.close()
    if not error:
        # on successful db insert, flash success
        flash('Artiste ' + request.form['name'] + ' was successfully listed!')
    else:
        # on unsuccessful db insert, flash error.
        flash('An error occurred. Artiste ' + request.form['name'] + ' could not be listed.')

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artiste ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    data = Show.query\
        .join(Venue, Show.venue_id == Venue.id)\
        .join(Artiste, Show.artiste_id == Artiste.id)\
        .add_columns(Venue.name.label('venue_name'),
                     Artiste.name.label('artiste_name'),
                     Artiste.image_link.label('artiste_image_link'),
                     Venue.id.label('venue_id'),
                     Artiste.id.label('artiste_id'),
                     Show.start_time)\
        .all()

    # data = [{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "artiste_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artiste_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artiste_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artiste_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artiste_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    # }]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    error = False
    try:
        newShow = Show(artiste_id=request.form.to_dict()['artiste_id'],
                       venue_id=request.form.to_dict()['venue_id'],
                       start_time=request.form.to_dict()['start_time'])
        db.session.add(newShow)
        db.session.commit()
    except():
        db.session.rollback()
        error = True
        print(sys.exc_info)
    finally:
        db.session.close()
    if not error:
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    else:
        # on unsuccessful db insert, flash error.
        flash('An error occurred. Show could not be listed.')

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
