from django.contrib import admin

try:
    from leaflet.admin import LeafletGeoAdmin as GeoAdmin
except ImportError:
    from django.contrib.gis.admin import OSMGeoAdmin as GeoAdmin


class PlaceAdmin(GeoAdmin, admin.ModelAdmin):
    list_display = ('name', 'city', 'state_province',)
    openlayers_url = '//cdnjs.cloudflare.com/ajax/libs/openlayers/2.12/OpenLayers.min.js'

    @staticmethod
    def get_address_fieldset():
        return ('Address', {
            'fields': (
                ('address_line1', 'address_line2', 'postal_code',),
                ('city', 'state_province', 'country',),
            ),
        })

    @staticmethod
    def get_geo_fieldset():
        return ('Geo', {
            'fields': (
                'centroid',
                #'polygon',
            ),
        })
