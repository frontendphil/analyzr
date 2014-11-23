import codecs

from datetime import timedelta

from parsr.models import Author, Revision, Branch

from django.db.models import Count

SIGNAVIO = 28

def md(branch=None, active=True, days=31):
    if not branch:
        branch = Branch.objects.get(pk=SIGNAVIO)

    revisions = Revision.objects.filter(branch=branch)

    if active:
        last_date = branch.analyzed_date - timedelta(days=days)

        revisions = revisions.filter(date__gte=last_date).distinct()

    authored = revisions.values("author").annotate(count=Count("id")).order_by("-count")

    revision_count = revisions.count()

    with codecs.open("contrib.csv", "wb", "utf-8") as f:
        for revision in authored:
            author = Author.objects.get(pk=revision["author"])

            line = u"%s,%s,%s\n" % (unicode(author.name), author.fake_name, round((100.0 * revision["count"]) / revision_count, 2))

            f.write(line)

def cls(branch=None, active=True, days=31):
    authors = None

    if not branch:
        branch = Branch.objects.get(pk=SIGNAVIO)
        authors = Author.objects.filter(revisions__branch=branch).distinct().order_by("fake_name")

    if not authors:
        authors = Author.objects.filter(revisions__branch=branch).distinct().order_by("name")

    if active:
        authors = authors.filter(revisions__date__gte=branch.analyzed_date - timedelta(days=days)).distinct()

    with codecs.open("classification.csv", "wb", "utf-8") as f:
        for author in authors:
            cls = author.classify(branch)

            f.write(u"%s,%s,%s,%s\n" % (unicode(author.name), author.fake_name, round(cls["frontend"] * 100, 2), round(cls["backend"] * 100, 2)))
