from datetime import datetime
from hashlib import md5
from os import path

import git
import hgapi as hg

from pysvn import Client, Revision
from pysvn import opt_revision_kind as revision_kind

from analyzr.settings import CHECKOUT_PATH


class Connector(object):

    @classmethod
    def get(cls, repo):
        kind = repo.kind

        if kind == "svn":
            return SVN(repo)

        if kind == "git":
            return Git(repo)

        if kind == "mercurial":
            return Mercurial(repo)

        return None

    def __init__(self, repo):
        self.repo = self.create_repo(repo)
        self.info = repo

    def create_repo(self, repo):
        raise NotImplementedError

    def analyze(self):
        raise NotImplementedError

    def parse_date(self, timestamp):
        return datetime.fromtimestamp(int(timestamp))


class Git(Connector):

    def create_repo(self, repo):
        folder = "%s/%s" % (CHECKOUT_PATH, md5(repo.url).hexdigest())

        if path.exists(folder):
            return git.Repo(folder)

        return git.Repo.clone_from(repo.url, folder)

    def parse(self, commit):
        stats = commit.stats

        for filename in stats.files.keys():
            revision = self.info.create_revision(commit.hexsha, filename)
            revision.set_author(commit.author)
            revision.set_date(self.parse_date(commit.committed_date))
            revision.save()

    def analyze(self):
        for commit in self.repo.iter_commits():
            self.parse(commit)


class SVN(Connector):

    def create_repo(self, repo):
        client = Client()

        client.callback_get_login = self.get_login(repo)

        return client

    def get_login(self, repo):
        def callback_get_login(realm, username, may_save):
            return not repo.anonymous, repo.user, repo.password, False

        return callback_get_login

    def get_head_revision(self):
        head = self.repo.info2(self.info.url,
            revision=Revision(revision_kind.head),
            recurse=False)

        name, info = head[0]

        revision = info["rev"]

        return revision.number

    def parse(self, identifier):
        files = self.repo.info2(self.info.url,
            revision=Revision(revision_kind.number, identifier))

        for filename, info in files:
            last_changed = info["last_changed_rev"]

            if not last_changed or not last_changed.number == identifier:
                continue

            revision = self.info.create_revision(identifier, filename)
            revision.set_author(info["last_changed_author"])
            revision.set_date(self.parse_date(info["last_changed_date"]))
            revision.save()

    def analyze(self):
        head = self.get_head_revision()

        while head > 0:
            self.parse(head)

            head = head - 1


class Mercurial(Connector):

    def create_repo(self, repo):
        return hg.Repo(repo)
