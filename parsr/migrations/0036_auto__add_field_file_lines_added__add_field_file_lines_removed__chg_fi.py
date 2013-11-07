# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'File.lines_added'
        db.add_column(u'parsr_file', 'lines_added',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'File.lines_removed'
        db.add_column(u'parsr_file', 'lines_removed',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


        # Changing field 'File.cyclomatic_complexity'
        db.alter_column(u'parsr_file', 'cyclomatic_complexity', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2))

        # Changing field 'File.halstead_difficulty'
        db.alter_column(u'parsr_file', 'halstead_difficulty', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2))

        # Changing field 'File.cyclomatic_complexity_delta'
        db.alter_column(u'parsr_file', 'cyclomatic_complexity_delta', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2))

        # Changing field 'File.halstead_effort'
        db.alter_column(u'parsr_file', 'halstead_effort', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2))

        # Changing field 'File.halstead_effort_delta'
        db.alter_column(u'parsr_file', 'halstead_effort_delta', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2))

        # Changing field 'File.halstead_volume_delta'
        db.alter_column(u'parsr_file', 'halstead_volume_delta', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2))

        # Changing field 'File.halstead_difficulty_delta'
        db.alter_column(u'parsr_file', 'halstead_difficulty_delta', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2))

        # Changing field 'File.halstead_volume'
        db.alter_column(u'parsr_file', 'halstead_volume', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2))

    def backwards(self, orm):
        # Deleting field 'File.lines_added'
        db.delete_column(u'parsr_file', 'lines_added')

        # Deleting field 'File.lines_removed'
        db.delete_column(u'parsr_file', 'lines_removed')


        # Changing field 'File.cyclomatic_complexity'
        db.alter_column(u'parsr_file', 'cyclomatic_complexity', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2))

        # Changing field 'File.halstead_difficulty'
        db.alter_column(u'parsr_file', 'halstead_difficulty', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2))

        # Changing field 'File.cyclomatic_complexity_delta'
        db.alter_column(u'parsr_file', 'cyclomatic_complexity_delta', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2))

        # Changing field 'File.halstead_effort'
        db.alter_column(u'parsr_file', 'halstead_effort', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2))

        # Changing field 'File.halstead_effort_delta'
        db.alter_column(u'parsr_file', 'halstead_effort_delta', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2))

        # Changing field 'File.halstead_volume_delta'
        db.alter_column(u'parsr_file', 'halstead_volume_delta', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2))

        # Changing field 'File.halstead_difficulty_delta'
        db.alter_column(u'parsr_file', 'halstead_difficulty_delta', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2))

        # Changing field 'File.halstead_volume'
        db.alter_column(u'parsr_file', 'halstead_volume', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2))

    models = {
        u'parsr.author': {
            'Meta': {'object_name': 'Author'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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
            'cyclomatic_complexity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'cyclomatic_complexity_delta': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'halstead_difficulty': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'halstead_difficulty_delta': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'halstead_effort': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'halstead_effort_delta': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'halstead_volume': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'halstead_volume_delta': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lines_added': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'lines_removed': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
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
            'next': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'previous'", 'null': 'True', 'to': u"orm['parsr.Revision']"}),
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