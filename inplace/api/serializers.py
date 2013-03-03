import geojson

from django.contrib.gis.geos.point import GEOSGeometry
from tastypie.serializers import Serializer


class GeoJSONSerializer(Serializer):
    formats = ['geojson',] # 'json']
    content_types = {
        'geojson': 'application/json',
        # TODO theoretically possible to use json, too, but impossibe to get
        #  geojson if this is included
        #'json': 'application/json',
    }

    def to_geojson(self, data, options={}):
        data = self.to_simple(data, options)

        if 'objects' in data:
            print len(data['objects'])
            return geojson.dumps(self._get_feature_collection(data['objects']))
        return data

    def _get_feature_collection(self, places):
        return geojson.FeatureCollection(
            features=[self._get_feature(place) for place in places],
        )

    def _get_feature(self, place):
        centroid = GEOSGeometry(place['centroid'])
        return geojson.Feature(
            place['id'],
            geometry=geojson.Point(
                coordinates=(centroid.x, centroid.y),
            ),
            properties=place,
        )


"""
An example of using the GeoJSONSerializer:

from tastypie.constants import ALL
from tastypie.resources import ModelResource

from places.api.serializers import GeoJSONSerializer
from pops.models import Building

# more complex filters: http://stackoverflow.com/questions/10021749/django-tastypie-advanced-filtering-how-to-do-complex-lookups-with-q-objects

# TODO for each subclass of Place
class BuildingResource(ModelResource):
    class Meta:
        default_format = 'geojson'
        filtering = {
            # TODO for all (public?) fields in model
            'address_line1': ALL,
        }
        queryset = Building.objects.all()
        serializer = GeoJSONSerializer()
"""
