# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.db.models import Count

class Migration(DataMigration):

    def forwards(self, orm):
        duplicates = orm.Author.objects.values("name").annotate(count=Count("id")).filter(count__gt=1)

        last_value = None
        ref = None

        for author in orm.Author.objects.filter(name__in=[item['name'] for item in duplicates]):
            if not author.name == last_value:
                last_value = author.name
                ref = author

                continue

            orm.Revision.objects.filter(author=author).update(author=ref)

            author.delete()


    def backwards(self, orm):
        raise RuntimeError("Cannot reverse this migration.")

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
    symmetrical = True
