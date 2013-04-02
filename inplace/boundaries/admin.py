from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from .models import Boundary, Layer


class BoundaryAdmin(OSMGeoAdmin, admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('label', 'layer', 'geometry',),
        }),
    )
    list_display = ('label', 'layer',)
    list_filters = ('layer',)


class LayerAdmin(OSMGeoAdmin, admin.ModelAdmin):
    list_display = ('name', 'source_file',)


admin.site.register(Boundary, BoundaryAdmin)
admin.site.register(Layer, LayerAdmin)
