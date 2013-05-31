import os
import tempfile
import zipfile

from django import forms
from django.forms.util import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis import gdal
from django.contrib.gis.geos import MultiPolygon, Polygon

from .models import Boundary, Layer


class BoundaryAddForm(forms.Form):
    label_field_name = forms.ChoiceField(choices=())
    layer = forms.ModelChoiceField(
        queryset=Layer.objects.all(),
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super(BoundaryAddForm, self).__init__(*args, **kwargs)

        # set initial label_field_name choices
        self.fields['label_field_name'].choices = self._get_label_field_name_choices()

    def add_boundaries(self):
        layer = self.cleaned_data['layer']
        label_field_name = self.cleaned_data['label_field_name']

        data_source = self._open_layer_file(layer)
        for feature in data_source[0]:
            geometry = feature.geom.transform(4326, clone=True).geos
            if isinstance(geometry, Polygon):
                geometry = MultiPolygon(geometry)
            boundary = Boundary(label=feature[label_field_name], layer=layer,
                                geometry=geometry)
            boundary.save()

    def _get_label_field_name_choices(self):
        ds = self._open_layer_file(self.initial['layer'])
        shplayer = ds[0]
        return [(f, self.display_name(shplayer, f)) for f in shplayer.fields]

    def display_name(self, layer, field):
        """
        Get a representation of the given field that includes example values.
        """
        examples = [str(f[field]) for f in layer[:min(3, len(layer))]]
        if len(examples) < len(layer):
            examples.append('...')
        ex = '%s: %s' % (field, ', '.join(examples))
        return ex

    def _open_layer_file(self, layer):
        """Unzip the layer file and return it as a GDAL DataSource"""
        tmp_dir, ds_name = open_zipped_shapefile(layer.source_file)
        ds = gdal.DataSource(os.path.join(tmp_dir, '%s.shp' % ds_name))
        return ds


class LayerUploadForm(forms.ModelForm):
    """
    Substantially borrowed from Dane Springmeyer's django-shapes:
        https://bitbucket.org/springmeyer/django-shapes/
    """

    source_file = forms.FileField(label=_('Upload a Zipped Shapefile'))

    class Meta:
        model = Layer

    def clean_source_file(self):
        f = self.cleaned_data['source_file']
        valid_shp, error = self.validate(f)
        if not valid_shp:
            raise ValidationError("A problem occured: %s" % error)
        return f

    def validate(self, filefield_data):
        """
        Validate the uploaded, zipped shapefile by unpacking to a temporary
        sandbox.
        """
        # create a temporary file to write the zip archive to
        tmp = tempfile.NamedTemporaryFile(suffix='.zip', mode = 'w')

        print 'tmp.name:', tmp.name

        # write zip to tmp sandbox
        self._write_file(tmp.name, filefield_data)

        is_valid, message = self._is_valid_shapefile(tmp.name)
        return is_valid, message

    def _write_file(self, filename, filefield_data):
        destination = open(filename, 'wb+')
        for chunk in filefield_data.chunks():
            destination.write(chunk)
        destination.close()

    def _check_zip_contents(self, ext, zip_file):
        if not True in [info.filename.endswith(ext) for info in zip_file.infolist()]:
            return False
        return True

    def _is_valid_shapefile(self, filename):
        if not zipfile.is_zipfile(filename):
            return False, 'That file is not a valid zip file'

        # create zip object
        zfile = zipfile.ZipFile(filename)

        # ensure proper file contents by extensions inside
        if not self._check_zip_contents('shp', zfile):
            return False, ('Found Zip Archive but no file with a .shp '
                           'extension found inside.')
        elif not self._check_zip_contents('prj', zfile):
            return False, ('You must supply a .prj file with the Shapefile to '
                           'indicate the projection.')
        elif not self._check_zip_contents('dbf', zfile):
            return False, ('You must supply a .dbf file with the Shapefile to '
                           'supply attribute data.')
        elif not self._check_zip_contents('shx', zfile):
            return False, ('You must supply a .shx file for the Shapefile to '
                           'have a valid index.')

        # okay, open it up!
        tmp_dir, ds_name = open_zipped_shapefile(filename)
        data_source = gdal.DataSource(os.path.join(tmp_dir, '%s.shp' % ds_name))

        # test for sane shapefile
        layer = data_source[0]
        if layer.test_capability('RandomRead'):
            if str(data_source.driver) == 'ESRI Shapefile':
                return True, None
            else:
                return False, ("Sorry, we've experienced a problem on our "
                               "server. Please try again later.")
        else:
            return False, ('Cannot read the shapefile, data is corrupted '
                           'inside the zip, please try to upload again')


def open_zipped_shapefile(filename):
    zfile = zipfile.ZipFile(filename)

    # unpack contents into tmp directory
    tmp_dir = tempfile.gettempdir()
    zfile.extractall(path=tmp_dir)
    for info in zfile.infolist():
        # skip directories in zipfile
        if info.filename[-1] == '/':
            continue
        data = zfile.read(info.filename)
        shp_part = os.path.join(tmp_dir, info.filename)
        fout = open(shp_part, "wb")
        fout.write(data)
        fout.close()

    # get the datasource name without extension
    ds_name = os.path.splitext(zfile.namelist()[0])[0]
    return tmp_dir, ds_name
