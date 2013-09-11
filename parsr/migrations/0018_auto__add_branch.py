# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Branch'
        db.create_table(u'parsr_branch', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'parsr', ['Branch'])

        # Adding M2M table for field branches on 'Repo'
        db.create_table(u'parsr_repo_branches', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('repo', models.ForeignKey(orm[u'parsr.repo'], null=False)),
            ('branch', models.ForeignKey(orm[u'parsr.branch'], null=False))
        ))
        db.create_unique(u'parsr_repo_branches', ['repo_id', 'branch_id'])


    def backwards(self, orm):
        # Deleting model 'Branch'
        db.delete_table(u'parsr_branch')

        # Removing M2M table for field branches on 'Repo'
        db.delete_table('parsr_repo_branches')


    models = {
        u'parsr.author': {
            'Meta': {'object_name': 'Author'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'repo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['parsr.Repo']", 'null': 'True', 'blank': 'True'})
        },
        u'parsr.branch': {
            'Meta': {'object_name': 'Branch'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'parsr.file': {
            'Meta': {'object_name': 'File'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'revision': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['parsr.Revision']"})
        },
        u'parsr.repo': {
            'Meta': {'object_name': 'Repo'},
            'analyzed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'analyzed_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'analyzing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'anonymous': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'branches': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['parsr.Branch']", 'symmetrical': 'False'}),
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