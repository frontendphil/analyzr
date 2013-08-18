# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Repo.anonymous'
        db.add_column(u'parsr_repo', 'anonymous',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


        # Changing field 'Repo.password'
        db.alter_column(u'parsr_repo', 'password', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Repo.user'
        db.alter_column(u'parsr_repo', 'user', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

    def backwards(self, orm):
        # Deleting field 'Repo.anonymous'
        db.delete_column(u'parsr_repo', 'anonymous')


        # Changing field 'Repo.password'
        db.alter_column(u'parsr_repo', 'password', self.gf('django.db.models.fields.CharField')(default=True, max_length=255))

        # Changing field 'Repo.user'
        db.alter_column(u'parsr_repo', 'user', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

    models = {
        u'parsr.repo': {
            'Meta': {'object_name': 'Repo'},
            'anonymous': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['parsr']