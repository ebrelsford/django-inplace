# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Boundary'
        db.create_table(u'boundaries_boundary', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('geometry', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
            ('layer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['boundaries.Layer'])),
        ))
        db.send_create_signal(u'boundaries', ['Boundary'])

        # Adding model 'Layer'
        db.create_table(u'boundaries_layer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('source_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'boundaries', ['Layer'])


    def backwards(self, orm):
        # Deleting model 'Boundary'
        db.delete_table(u'boundaries_boundary')

        # Deleting model 'Layer'
        db.delete_table(u'boundaries_layer')


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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'source_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['boundaries']