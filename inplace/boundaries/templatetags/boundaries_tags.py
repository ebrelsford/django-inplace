from django.contrib.gis.geos import Point

from classytags.arguments import Argument
from classytags.core import Options
from classytags.helpers import AsTag


class BaseGetBoundaryTag(AsTag):
    """
    A base tag for finding the boundary that a point is in.
    """
    options = Options(
        Argument('lat'),
        Argument('lon'),
        'as',
        Argument('varname', resolve=False, required=False),
    )

    def get_boundary_model(self):
        raise NotImplementedError('Implement get_boundary_model()')

    def get_value(self, context, lat, lon):
        boundary_model = self.get_boundary_model()
        try:
            return boundary_model.objects.get(
                geometry__contains=Point(lon, lat, srid=4326)
            )
        except boundary_model.DoesNotExist:
            return None
        except boundary_model.MultipleObjectsReturned:
            return None


class BaseAllBoundariesTag(AsTag):
    options = Options(
        'as',
        Argument('varname', required=True, resolve=False),
    )

    def get_value(self, context):
        raise NotImplementedError('Implement get_value()')
