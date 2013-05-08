"""
An app that lets admins upload boundary files (shapefiles) that can be
configured as boundaries on the front- and backend for selecting Places.

"""
from django.contrib.gis.db import models
from django.contrib.gis.geos import MultiPolygon
from django.utils.translation import ugettext_lazy as _


class BoundaryManager(models.GeoManager):

    def order_by_label_numeric(self, *args, **kwargs):
        """Attempt to sort by labels as if they are numeric."""
        qs = self.get_query_set().filter(*args, **kwargs)
        try:
            return sorted(qs, key=lambda b: int(b.label))
        except Exception:
            return qs


class Boundary(models.Model):

    objects = BoundaryManager()

    label = models.CharField(_('label'),
        max_length=256,
    )

    geometry = models.MultiPolygonField(_('geometry'))

    simplified_geometry = models.MultiPolygonField(_('simplified geometry'),
        blank=True,
        null=True,
    )

    layer = models.ForeignKey('Layer',
        verbose_name=_('layer'),
    )

    def __unicode__(self):
        return '%s %s' % (self.layer.name, self.label)

    def save(self, *args, **kwargs):
        # Simplify enough to reduce size significantly without having an
        # obvious effect on the geometry
        simplified = MultiPolygon(self.geometry.simplify(tolerance=0.0001))
        self.simplified_geometry = simplified

        super(Boundary, self).save(*args, **kwargs)

    class Meta:
        ordering = ('layer__name', 'label',)
        verbose_name_plural = _('boundaries')


class Layer(models.Model):

    objects = models.GeoManager()

    # TODO only allow alpha and spaces
    name = models.CharField(_('name'),
        max_length=256,
        unique=True,
    )

    source_file = models.FileField(_('source file'),
        upload_to='places_boundary_layers',
    )

    def __unicode__(self):
        return self.name
