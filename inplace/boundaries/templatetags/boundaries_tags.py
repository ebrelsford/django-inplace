from django import template
from django.contrib.gis.geos import Point

from classytags.arguments import Argument
from classytags.core import Options
from classytags.helpers import AsTag

from ..models import Boundary


register = template.Library()


class BaseGetBoundaryTag(AsTag):
    """
    A base tag for finding the boundary that a point is in.
    """
    options = Options(
        Argument('lat'),
        Argument('lon'),
        Argument('allow_multiple', required=False),
        'as',
        Argument('varname', resolve=False, required=False),
    )

    def get_boundary_model(self):
        raise NotImplementedError('Implement get_boundary_model()')

    def get_value(self, context, lat, lon, allow_multiple):
        boundary_model = self.get_boundary_model()
        try:
            kwargs = { 'geometry__contains': Point(lon, lat, srid=4326) }
            if allow_multiple:
                return boundary_model.objects.filter(**kwargs)
            return boundary_model.objects.get(**kwargs)
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


class AllBoundaries(AsTag):
    options = Options(
        Argument('layer'),
        'as',
        Argument('varname', required=True, resolve=False),
    )

    def get_value(self, context, layer):
        return Boundary.objects.filter(layer__name=layer).order_by('label')


class SortIntLabels(AsTag):
    """Sort the given boundaries while assuming the labels are integers."""
    options = Options(
        Argument('boundaries', required=True, resolve=True),
        'as',
        Argument('varname', required=True, resolve=False),
    )

    def get_value(self, context, boundaries):
        return sorted(boundaries, key=lambda d: int(d.label))


register.tag(AllBoundaries)
register.tag(SortIntLabels)
