from datetime import datetime

from django.db import models

from parsr.connectors import Connector

class Repo(models.Model):

    TYPES = (
        ("svn", "Subversion"),
        ("git", "Git"),
        ("mercurial", "Mercurial")
    )

    url = models.CharField(max_length=255)
    kind = models.CharField(max_length=255, choices=TYPES)

    anonymous = models.BooleanField(default=True)

    analyzed = models.BooleanField(default=False)
    analyzing = models.BooleanField(default=False)
    analyzed_date = models.DateTimeField(null=True, blank=True)

    user = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return "%s repository at: %s" % (self.kind, self.url)

    def analyze(self):
        self.analyzed = False
        self.analyzing = True
        self.save()

        connector = Connector.get(self)
        connector.analyze()

        self.analyzing = False
        self.analyzed = True
        self.analyzed_date = datetime.now()
        self.save()

    def create_revision(self, identifier, filename):
        revision, created = Revision.objects.get_or_create(
            repo=self,
            identifier=identifier
        )

        revision.add_file(filename)

        return revision

    def revision_count(self):
        return self.revision_set.count()

    def author_count(self):
        return self.author_set.count()

    def age(self):
        if not self.analyzed or self.revision_set.count() == 0:
            return "n/a"

        start = self.revision_set.order_by("date")[0:1][0]
        end = self.revision_set.order_by("-date")[0:1][0]

        return end.date - start.date

    def authors(self):
        authors = Author.objects.filter(repo=self)

        return sorted(authors, key=lambda author: author.revision_count())[::-1]

class Revision(models.Model):

    repo = models.ForeignKey("Repo")

    identifier = models.CharField(max_length=255)
    author = models.ForeignKey("Author", null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return "%s created by %s in %s" % (self.identifier, self.author, self.repo)

    def add_file(self, filename):
        File.objects.get_or_create(revision=self, name=filename)

    def set_author(self, name):
        author, created = Author.objects.get_or_create(
            repo=self.repo,
            name=name
        )

        self.author = author

    def set_date(self, date):
        self.date = date


class File(models.Model):

    revision = models.ForeignKey("Revision")

    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Author(models.Model):

    repo = models.ForeignKey("Repo", null=True, blank=True)

    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    def revision_count(self):
        return Revision.objects.filter(author=self, repo=self.repo).count()
