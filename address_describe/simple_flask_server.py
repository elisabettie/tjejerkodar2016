import os
import time
import geocoder
import requests

from flask import Flask, render_template

# 44520745 user ID - Insta
INSTA_ACCESS_TOKEN = '44520745.e029fea.3bd7fe5084bd4ef4aadd305e5f9cbb11'
WEATHER_API_KEY = 'abb7173160282779d2a544a9e4840651'
GOOGLE_MAPS_STATIC_API_KEY = 'AIzaSyBcmFyL__dYYSEpGiIZMaWGBpv0uZzouZo'
GOOGLE_MAPS_STREETVIEW_API_KEY = 'AIzaSyDeJLIXPmL3KKvgwdaAUFJ3TMwTz8wATTU'
GOOGLE_MAPS_GEOCODING_API_KEY = 'AIzaSyA-_uQ0ZLawwDEElMASHdpHN6QQz9hpw0M'
# Better way (yet still kinda bad) to load secrets
# secrets = dict()
# with open("SECRETS.json") as f:
#     secrets = json.loads(f.read())

# 'static_folder' is used for serving static files
proj_dir = os.path.abspath(os.path.dirname(__file__))
static_folder = os.path.join(proj_dir, 'static')


app = Flask(__name__)
address = "Stockholm, Sweden"


def get_photos(lati, longi):
    '''
    This method queries Instagram 'media/search' API endpoint for
    a given lati/longi and returns the reply as a json()
    '''
    insta_address = "https://api.instagram.com/v1/media/search?lat={}&lng={}&access_token={}".format(lati,longi,INSTA_ACCESS_TOKEN)
    photos = requests.get(insta_address)
    return photos.json()
    pass


def _get_weather(lati, longi):
    '''
    This function queries the forcast.io '/forcast' API endpoint for
    a given lati/longi and processes the data to return a single string
    which is a description of the current temperature and summary of
    daily forecast
    '''
    forecast_address = "https://api.forecast.io/forecast/{}/{},{}".format(WEATHER_API_KEY,lati,longi)
    r = requests.get(forecast_address)
    weather = r.json()
# gets current temperature 
    currently = weather["currently"]
    temperature = currently["temperature"]

    # gets the daily data for whole week
    daily = weather["daily"]["data"]
    
    # gets daily data for today
    today = daily[0]
    
    # gets todays summary
    today_summary = today["summary"]
    return "The temperature is {} Fahrenheit and the forcast is {}".format(temperature, today_summary)

def _get_lati_longi(address):
    '''
    This function takes an address string and return the lati/longi for
    that address
    '''
    g = geocoder.google(address)
    lat_and_long = g.latlng
    lati = lat_and_long[0]
    longi = lat_and_long[1]
    return lati, longi
    pass

def _save_static_file(name, content):
    '''
    This fucntion takes a name of a file to create in the
    /static folder (which can be used to load images) and
    write the 'content' given to it.

    This is useful if an API gives you a binary content
    '''

    filename = os.path.join(static_folder, name)

    # Delete it if exists
    try:
        os.remove(filename)
    except OSError:
        pass

    # Write content to file
    with open(filename, 'w+b') as f:
        f.write(content)

def get_static_map(lati, longi):
    '''
    This function queries the google maps '/staticmap' API endpoint for
    a given lati/longi gets a static map image. Since the API returns
    the image itself, this funciton need to save that image to disk in
    the /static folder and then return a STRING which is
    /static/<image_name>?<random_number>
    The latter is to avoid browser caching.
    '''
    # r = requests.get()
    map_image = "https://maps.googleapis.com/maps/api/staticmap?center={},{}&zoom=13&size=600x400&key={}".format(lati,longi, GOOGLE_MAPS_GEOCODING_API_KEY)
    # _save_static_file('map.jpg', r.content)  
    # r is the result of requests.get() from the google static maps API
    r = requests.get(map_image)
    _save_static_file('map.jpg' , r.content)
    return '/static/map.jpg?{}'.format(time.time())
    pass


def get_streetview(lati, longi):
    '''
    This function queries the google maps '/streetview' API endpoint for
    a given lati/longi gets a static map image. Since the API returns
    the image itself, this funciton need to save that image to disk in
    the /static folder and then return a STRING which is
    /static/<image_name>?<random_number>
    The latter is to avoid browser caching.
    '''

    # r = requests.get(...)
     # r is the result of requests.get() from the google streetview API
    streetview_image = "https://maps.googleapis.com/maps/api/streetview?location={},{}&size=600x400&key={}".format(lati,longi,GOOGLE_MAPS_STREETVIEW_API_KEY)
    r = requests.get(streetview_image)
    _save_static_file('street.jpg', r.content)
    return '/static/street.jpg?{}'.format(time.time())


@app.route('/')
def index():
    return render_template('./index.html')

@app.route('/describe/<address>')
def describe_address(address):
    lati, longi = _get_lati_longi(address)

    # This is just text describing the weather
    weather = _get_weather(lati, longi)

    # This is a list jsons which has a )
    photos_urls = get_photos(lati, longi)

    # These are filenames for a jpg file containing the image
    static_map = get_static_map(lati, longi)
    street_view = get_streetview(lati, longi)

    return render_template('./address.html', address=address.capitalize(),
                           lati=lati, longi=longi, weather=weather,
                           photos=photos_urls, static_map=static_map,
                           street_view=street_view)


if __name__ == "__main__":
    app.run(port=8080, debug=True)