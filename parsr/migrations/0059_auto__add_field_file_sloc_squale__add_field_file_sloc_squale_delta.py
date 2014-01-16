# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'File.sloc_squale'
        db.add_column(u'parsr_file', 'sloc_squale',
                      self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=15, decimal_places=2),
                      keep_default=False)

        # Adding field 'File.sloc_squale_delta'
        db.add_column(u'parsr_file', 'sloc_squale_delta',
                      self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=15, decimal_places=2),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'File.sloc_squale'
        db.delete_column(u'parsr_file', 'sloc_squale')

        # Deleting field 'File.sloc_squale_delta'
        db.delete_column(u'parsr_file', 'sloc_squale_delta')


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
            'last_analyze_error': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'last_measure_error': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'measured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'measured_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'measuring': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'repo': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'branches'", 'null': 'True', 'to': u"orm['parsr.Repo']"}),
            'revision_count': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'parsr.file': {
            'Meta': {'object_name': 'File'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['parsr.Author']", 'null': 'True'}),
            'change_type': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'copy_of': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['parsr.File']", 'null': 'True'}),
            'cyclomatic_complexity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'cyclomatic_complexity_delta': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'fan_in': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'fan_in_delta': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'fan_out': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'fan_out_delta': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'halstead_difficulty': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'halstead_difficulty_delta': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'halstead_volume': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'halstead_volume_delta': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'hk': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'hk_delta': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lines_added': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'lines_removed': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'package': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pkg': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'files'", 'null': 'True', 'to': u"orm['parsr.Package']"}),
            'revision': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['parsr.Revision']"}),
            'sloc': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sloc_delta': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sloc_squale': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'sloc_squale_delta': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'})
        },
        u'parsr.package': {
            'Meta': {'object_name': 'Package'},
            'branch': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['parsr.Branch']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'left': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': u"orm['parsr.Package']"}),
            'right': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'parsr.repo': {
            'Meta': {'object_name': 'Repo'},
            'anonymous': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ignored_files': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'ignored_folders': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'timezone': ('timezone_field.fields.TimeZoneField', [], {'default': "'Europe/Berlin'"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'parsr.revision': {
            'Meta': {'object_name': 'Revision'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['parsr.Author']", 'null': 'True'}),
            'branch': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['parsr.Branch']", 'null': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'day': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'hour': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'measured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'minute': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'month': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'next': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'previous'", 'null': 'True', 'to': u"orm['parsr.Revision']"}),
            'weekday': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        }
    }

    complete_apps = ['parsr']