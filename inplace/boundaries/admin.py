from django.contrib import admin

try:
    from leaflet.admin import LeafletGeoAdmin as GeoAdmin
except ImportError:
    from django.contrib.gis.admin import OSMGeoAdmin as GeoAdmin

from .models import Boundary, Layer


class BoundaryAdmin(GeoAdmin, admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('label', 'layer', 'geometry',),
        }),
    )
    list_display = ('label', 'layer',)
    list_filters = ('layer',)


class LayerAdmin(GeoAdmin, admin.ModelAdmin):
    list_display = ('name', 'source_file',)


admin.site.register(Boundary, BoundaryAdmin)
admin.site.register(Layer, LayerAdmin)
