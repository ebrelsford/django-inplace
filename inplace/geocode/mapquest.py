import json
from urllib import urlencode
from urllib2 import urlopen

from django.conf import settings


BASE_URL = 'http://www.mapquestapi.com/geocoding/v1/address?'

def geocode(address):
    url = BASE_URL + 'key=%s&' % settings.PLACES_MAPQUEST_KEY + urlencode({
        'location': address,
    })
    geocoded = json.load(urlopen(url))

    try:
        loc = geocoded['results'][0]['locations'][0]
        return (loc['latLng']['lng'], loc['latLng']['lat'])
    except Exception:
        return (None, None)
