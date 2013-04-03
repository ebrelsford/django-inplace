# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'Layer', fields ['name']
        db.create_unique(u'boundaries_layer', ['name'])


    def backwards(self, orm):
        # Removing unique constraint on 'Layer', fields ['name']
        db.delete_unique(u'boundaries_layer', ['name'])


    models = {
        u'boundaries.boundary': {
            'Meta': {'object_name': 'Boundary'},
            'geometry': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'layer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['boundaries.Layer']"})
        },
        u'boundaries.layer': {
            'Meta': {'object_name': 'Layer'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'source_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['boundaries']