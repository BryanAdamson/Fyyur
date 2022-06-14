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


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#
def format_datetime(value, format_type='medium'):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
    if format_type == 'full':
        format_type = "EEEE MMMM, d, y 'at' h:mma"
    elif format_type == 'medium':
        format_type = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format_type, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#
#  Home
#  ----------------------------------------------------------------
@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
#  Create
#  ----------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
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
        # on unsuccessful db insert, flash error.
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

    return render_template('pages/home.html')


#  Read
#  ----------
@app.route('/venues')
def venues():
    allVenues = db.session.query(Venue.city, Venue.state).distinct().all()

    data = []

    for area in allVenues:

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

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    responseData = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
    response = {'count': len(responseData), 'data': responseData}

    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    realData = Venue.query.get(venue_id)
    data = {'id': realData.id,
            'name': realData.name,
            'address': realData.address,
            'phone': realData.phone,
            'genres': realData.genres,
            'website': realData.website,
            'facebook_link': realData.facebook_link,
            'seeking_talent': realData.seeking_talent,
            'seeking_description': realData.seeking_description,
            'image_link': realData.image_link,
            'upcoming_shows': Show.query.join(Artiste, Show.artiste_id == Artiste.id).add_columns(
                Show.venue_id,
                Artiste.id.label('artiste_id'),
                Artiste.name.label('artiste_name'),
                Artiste.image_link.label('artiste_image_link'),
                Show.start_time
            ).filter(Show.start_time >= datetime.now(), Show.venue_id == venue_id),
            'past_shows': Show.query.join(Artiste, Show.artiste_id == Artiste.id).add_columns(
                Show.venue_id,
                Artiste.id.label('artiste_id'),
                Artiste.name.label('artiste_name'),
                Artiste.image_link.label('artiste_image_link'),
                Show.start_time
            ).filter(Show.start_time < datetime.now(), Show.venue_id == venue_id)}
    data['upcoming_shows_count'] = data['upcoming_shows'].count()
    data['past_shows_count'] = data['past_shows'].count()

    return render_template('pages/show_venue.html', venue=data)


#  Update
#  ----------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
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
        # on unsuccessful db insert, flash error.
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')

    return redirect(url_for('show_venue', venue_id=venue_id))


#  Delete
#  ----------
@app.route('/venues/<venue_id>/delete')
def delete_venue(venue_id):
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
        # on unsuccessful db delete, flash an error instead.
        flash('An error occurred. Venue could not be deleted.')

    return render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------
#  Create
#  ----------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
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

    return render_template('pages/home.html')


#  Read
#  ----------
@app.route('/artists')
def artists():
    data = Artiste.query.all()

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    responseData = Artiste.query.add_columns(Artiste.id, Artiste.name).filter(
        Artiste.name.ilike('%' + search_term + '%')).all()
    response = {'count': len(responseData), 'data': responseData}

    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    realData = Artiste.query.get(artist_id)
    data = {'id': realData.id,
            'name': realData.name,
            'phone': realData.phone,
            'website': realData.website,
            'genres': realData.genres,
            'facebook_link': realData.facebook_link,
            'seeking_venue': realData.seeking_venue,
            'seeking_description': realData.seeking_description,
            'image_link': realData.image_link,
            'upcoming_shows': Show.query.join(Venue, Show.venue_id == Venue.id).add_columns(
                Show.artiste_id,
                Venue.id.label('venue_id'),
                Venue.name.label('venue_name'),
                Venue.image_link.label('venue_image_link'),
                Show.start_time
            ).filter(Show.start_time >= datetime.now(), Show.artiste_id == artist_id),
            'past_shows': Show.query.join(Venue, Show.venue_id == Venue.id).add_columns(
                Show.artiste_id,
                Venue.id.label('venue_id'),
                Venue.name.label('venue_name'),
                Venue.image_link.label('venue_image_link'),
                Show.start_time
            ).filter(Show.start_time < datetime.now(), Show.artiste_id == artist_id)}
    data['upcoming_shows_count'] = data['upcoming_shows'].count()
    data['past_shows_count'] = data['past_shows'].count()

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artiste = Artiste.query.get(artist_id)

    return render_template('forms/edit_artist.html', form=form, artist=artiste)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    try:
        artiste = Artiste.query.get(artist_id)
        artiste.name = request.form.to_dict()['name']
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


#  Delete
#  ----------


#  Shows
#  ----------------------------------------------------------------
#  Create
#  ----------
@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
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

    return render_template('pages/home.html')


#  Read
#  ----------
@app.route('/shows')
def shows():
    data = Show.query \
        .join(Venue, Show.venue_id == Venue.id) \
        .join(Artiste, Show.artiste_id == Artiste.id) \
        .add_columns(Venue.name.label('venue_name'),
                     Artiste.name.label('artiste_name'),
                     Artiste.image_link.label('artiste_image_link'),
                     Venue.id.label('venue_id'),
                     Artiste.id.label('artiste_id'),
                     Show.start_time) \
        .all()

    return render_template('pages/shows.html', shows=data)


#  Update
#  ----------


#  Delete
#  ----------


# ----------------------------------------------------------------------------#
# Error Handlers
# ----------------------------------------------------------------------------#
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
if __name__ == '__main__':
    app.run()
