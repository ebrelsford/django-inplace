import geojson
import json

from django.contrib.gis.shortcuts import render_to_kml
from django.http import HttpResponse
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import BaseDetailView, DetailView
from django.views.generic.list import BaseListView, ListView


def module_name():
    return __name__.split('.')[0]


class JSONResponseView(View):
    response_class = HttpResponse

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def render_to_response(self, context, **response_kwargs):
        """Simple render to JSON"""
        return self.response_class(
            json.json.dumps(self.get_context_data(**self.kwargs),
                            cls=json.DjangoJSONEncoder, ensure_ascii=False),
            mimetype='application/json',
        )


class GeoJSONResponseMixin(object):
    """A mixin that renders Places as GeoJSON."""
    response_class = HttpResponse

    def get_properties(self, place):
        """
        The properties that will be added to the given Place's GeoJSON feature.
        """
        return {
            'id': place.pk,
            'name': place.name,
            'popup_url': place.get_popup_url(),
        }

    def get_feature(self, place):
        """
        Get a Feature for a Place.
        """
        if place.polygon:
            geometry = place.polygon
        else:
            geometry = place.centroid
        return geojson.Feature(
            place.id,
            geometry=json.loads(geometry.geojson),
            properties=self.get_properties(place),
        )

    def get_features(self):
        """
        Get a list of Features given our queryset.
        """
        try:
            places = [self.get_object(),]
        except Exception:
            places = self.get_queryset()
        return [self.get_feature(place) for place in places]

    def get_feature_collection(self):
        """
        Get a FeatureCollection for our Places.
        """
        return geojson.FeatureCollection(features=self.get_features())

    def render_to_response(self, context, **response_kwargs):
        """
        Render to GeoJSON.
        """
        return self.response_class(
            geojson.dumps(self.get_feature_collection(), separators=(',', ':')),
            mimetype='application/json',
        )


class GeoJSONListView(GeoJSONResponseMixin, BaseListView):
    pass


class GeoJSONDetailView(BaseDetailView, GeoJSONResponseMixin):
    pass


class DefaultTemplateMixin(TemplateResponseMixin):
    default_template_name = None

    def get_template_names(self):
        names = super(DefaultTemplateMixin, self).get_template_names()

        # fall back on default
        if self.default_template_name:
            names.append(self.default_template_name)
        return names


class AddAppModelMixin(object):

    def _get_app_name(self):
        return self.model._meta.app_label

    def _get_model_name(self):
        return self.model.__name__.lower()

    def get_context_data(self, **kwargs):
        context = super(AddAppModelMixin, self).get_context_data(**kwargs)
        context.update({
            'app_name': self._get_app_name(),
            'model': self.model,
            'model_name': self._get_model_name(),
        })
        return context


class PlacesDetailView(AddAppModelMixin, DetailView):

    def get_template_names(self):
        return [
            '%s/%s/%s%s.html' % (module_name(), self._get_app_name(),
                                 self._get_model_name(),
                                 self.template_name_suffix),
            '%s/detail.html' % module_name(),
        ]


class PlacesPopupView(AddAppModelMixin, DetailView):
    template_name_suffix='_popup'

    def get_template_names(self):
        return [
            '%s/%s/%s%s.html' % (module_name(), self._get_app_name(),
                                 self._get_model_name(),
                                 self.template_name_suffix),
            '%s/popup.html' % module_name(),
        ]


class PlacesListView(AddAppModelMixin, DefaultTemplateMixin, ListView):
    default_template_name = '%s/list.html' % module_name()


class PlacesGeoJSONListView(GeoJSONListView):

    def get_queryset(self):
        qs = super(PlacesGeoJSONListView, self).get_queryset()
        return qs.filter(centroid__isnull=False)


class PlacesGeoJSONDetailView(GeoJSONDetailView):
    pass


class KMLView(View):
    response_class = HttpResponse

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def render_to_response(self, context, **response_kwargs):
        # Expects 'places' in context, Place models fetched with .kml()
        response = render_to_kml('gis/kml/placemarks.kml', context)

        # Add header to download as an attachment
        if context.get('download', False):
            response['Content-Disposition'] = (
                'attachment; filename="%s.kml"' % context.get('filename', 'places')
            )
        return response
