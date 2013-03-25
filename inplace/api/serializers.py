import geojson

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
        data['objects'] = [self._get_feature_collection(data['objects']),]
        return geojson.dumps(data)

    def _get_feature_collection(self, places):
        return geojson.FeatureCollection(
            features=[self._get_feature(place) for place in places],
        )

    def _get_feature(self, place):
        return geojson.Feature(
            place['id'],
            geometry=place['centroid'],
            properties=place,
        )


"""
An example of using the GeoJSONSerializer:

from tastypie.constants import ALL
from tastypie.contrib.gis.resources import ModelResource

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
