import geojson
import json

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import Http404
from django.views.generic import CreateView, FormView

from braces.views import LoginRequiredMixin, PermissionRequiredMixin

from ..views import GeoJSONResponseMixin, JSONResponseView
from .forms import BoundaryAddForm, LayerUploadForm
from .models import Layer


class LayerUploadView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    form_class = LayerUploadForm
    permission_required = ('boundaries.add_layer',)
    template_name = 'inplace/boundaries/layer_upload.html'

    def get_success_url(self):
        messages.success(self.request, 'Successfully uploaded shapefile.')
        return reverse('inplace:boundary_add', kwargs={'pk': self.object.pk})


class BoundaryAddView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    form_class = BoundaryAddForm
    permission_required = ('boundaries.add_boundary',)
    template_name = 'inplace/boundaries/boundary_add.html'

    def _get_layer(self):
        try:
            return self.layer
        except Exception:
            self.layer = Layer.objects.get(pk=self.kwargs['pk'])
        return self.layer

    def form_valid(self, form):
        form.add_boundaries()
        return super(BoundaryAddView, self).form_valid(form)

    def get_initial(self):
        initial = super(BoundaryAddView, self).get_initial()
        initial['layer'] = self._get_layer()
        return initial

    def get_success_url(self):
        layer = self._get_layer()
        messages.success(self.request,
                         'Successfully added boundaries to layer %s' % layer.name)
        return reverse('inplace:boundary_add', kwargs={'pk': layer.pk})


class LayerView(GeoJSONResponseMixin, JSONResponseView):

    def get_context_data(self, **kwargs):
        return self.get_features()

    def get_features(self):
        try:
            layer = Layer.objects.get(
                name__iexact=self.kwargs['name'],
            )
        except Exception:
            raise Http404

        features = []
        for boundary in layer.boundary_set.all():
            features.append(geojson.Feature(
                boundary.pk,
                geometry=json.loads(boundary.simplified_geometry.geojson),
                properties={
                    'boundary_label': boundary.label,
                }
            ))
        return features
