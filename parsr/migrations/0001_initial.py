# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Repo'
        db.create_table(u'parsr_repo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'parsr', ['Repo'])


    def backwards(self, orm):
        # Deleting model 'Repo'
        db.delete_table(u'parsr_repo')


    models = {
        u'parsr.repo': {
            'Meta': {'object_name': 'Repo'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['parsr']