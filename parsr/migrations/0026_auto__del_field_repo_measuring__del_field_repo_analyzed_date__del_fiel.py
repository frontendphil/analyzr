# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Repo.measuring'
        db.delete_column(u'parsr_repo', 'measuring')

        # Deleting field 'Repo.analyzed_date'
        db.delete_column(u'parsr_repo', 'analyzed_date')

        # Deleting field 'Repo.analyzing'
        db.delete_column(u'parsr_repo', 'analyzing')

        # Deleting field 'Repo.analyzed'
        db.delete_column(u'parsr_repo', 'analyzed')

        # Deleting field 'Repo.measured'
        db.delete_column(u'parsr_repo', 'measured')

        # Adding field 'Branch.analyzed'
        db.add_column(u'parsr_branch', 'analyzed',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Branch.analyzing'
        db.add_column(u'parsr_branch', 'analyzing',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Branch.analyzed_date'
        db.add_column(u'parsr_branch', 'analyzed_date',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Branch.measured'
        db.add_column(u'parsr_branch', 'measured',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Branch.measuring'
        db.add_column(u'parsr_branch', 'measuring',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Repo.measuring'
        db.add_column(u'parsr_repo', 'measuring',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Repo.analyzed_date'
        db.add_column(u'parsr_repo', 'analyzed_date',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Repo.analyzing'
        db.add_column(u'parsr_repo', 'analyzing',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Repo.analyzed'
        db.add_column(u'parsr_repo', 'analyzed',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Repo.measured'
        db.add_column(u'parsr_repo', 'measured',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Deleting field 'Branch.analyzed'
        db.delete_column(u'parsr_branch', 'analyzed')

        # Deleting field 'Branch.analyzing'
        db.delete_column(u'parsr_branch', 'analyzing')

        # Deleting field 'Branch.analyzed_date'
        db.delete_column(u'parsr_branch', 'analyzed_date')

        # Deleting field 'Branch.measured'
        db.delete_column(u'parsr_branch', 'measured')

        # Deleting field 'Branch.measuring'
        db.delete_column(u'parsr_branch', 'measuring')


    models = {
        u'parsr.author': {
            'Meta': {'object_name': 'Author'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'repo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['parsr.Repo']", 'null': 'True', 'blank': 'True'})
        },
        u'parsr.branch': {
            'Meta': {'object_name': 'Branch'},
            'analyzed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'analyzed_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'analyzing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'measured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'measuring': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'repo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['parsr.Repo']", 'null': 'True'})
        },
        u'parsr.file': {
            'Meta': {'object_name': 'File'},
            'change_type': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'copy_of': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['parsr.File']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'revision': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['parsr.Revision']"})
        },
        u'parsr.repo': {
            'Meta': {'object_name': 'Repo'},
            'anonymous': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'timezone': ('timezone_field.fields.TimeZoneField', [], {'default': "'Europe/Berlin'"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'parsr.revision': {
            'Meta': {'object_name': 'Revision'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['parsr.Author']", 'null': 'True', 'blank': 'True'}),
            'branch': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['parsr.Branch']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'repo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['parsr.Repo']"}),
            'revision_date': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['parsr.RevisionDate']", 'null': 'True', 'blank': 'True'})
        },
        u'parsr.revisiondate': {
            'Meta': {'object_name': 'RevisionDate'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'day': ('django.db.models.fields.IntegerField', [], {}),
            'hour': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minute': ('django.db.models.fields.IntegerField', [], {}),
            'month': ('django.db.models.fields.IntegerField', [], {}),
            'weekday': ('django.db.models.fields.IntegerField', [], {}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['parsr']