# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Repo.kind'
        db.add_column(u'parsr_repo', 'kind',
                      self.gf('django.db.models.fields.CharField')(default='svn', max_length=255),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Repo.kind'
        db.delete_column(u'parsr_repo', 'kind')


    models = {
        u'parsr.repo': {
            'Meta': {'object_name': 'Repo'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['parsr']