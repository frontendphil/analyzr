from datetime import datetime
from hashlib import md5
from os import walk

import os
import git
import hgapi as hg

from pysvn import Client, Revision
from pysvn import opt_revision_kind as revision_kind

from mimetypes import guess_type

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

    def analyze(self, branch):
        raise NotImplementedError

    def get_branches(self):
        raise NotImplementedError

    def get_repo_path(self, repo):
        return "%s/%s" % (CHECKOUT_PATH, md5(repo.url).hexdigest())

    def folder_is_valid(self, name):
        return True

    def update(self, path):
        pass

    def get_file_statistics(self, path=None, update=True):
        if not path:
            path = self.get_repo_path(self.info)

        if update:
            self.update(path)

        for folder, folders, files in walk(path):
            for folder in folders:
                if not self.folder_is_valid(folder):
                    continue

                folder = "%s/%s" % (path, folder)

                self.get_file_statistics(folder, False)

            for name in files:
                if name.startswith("."):
                    continue

                mimetype, encoding = guess_type(name)
                self.info.add_mime_info(mimetype)

    def parse_date(self, timestamp):
        return datetime.fromtimestamp(int(timestamp))


class Git(Connector):

    def create_repo(self, repo):
        folder = self.get_repo_path(repo)

        if os.path.exists(folder):
            return git.Repo(folder)

        return git.Repo.clone_from(repo.url, folder)

    def parse(self, commit):
        stats = commit.stats

        for filename in stats.files.keys():
            revision = self.info.create_revision(commit.hexsha, filename)
            revision.set_author(commit.author)
            revision.set_date(self.parse_date(commit.committed_date))
            revision.save()

    def analyze(self, branch="master"):
        for commit in self.repo.iter_commits():
            self.parse(commit)

    def get_branches(self):
        result = []

        for info in self.repo.remotes.origin.fetch():
            result.append((info.name, info.ref.path))

        return result

    def folder_is_valid(self, name):
        return not name == ".git"


class SVN(Connector):

    def create_repo(self, repo):
        client = Client()

        client.callback_get_login = self.get_login(repo)
        client.callback_ssl_server_trust_prompt = self.get_trust(repo)

        return client

    def get_trust(self, repo):
        def callback_ssl_trust_prompt(trust_dict):
            return not repo.anonymous, trust_dict["failures"], False

        return callback_ssl_trust_prompt

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
        log = self.repo.log(self.info.url,
            revision_start=Revision(revision_kind.number, identifier),
            revision_end=Revision(revision_kind.number, identifier),
            discover_changed_paths=True,
            limit=0)

        if len(log) == 0:
            # Revision does not affect current branch

            return

        log = log[0]

        for filename in log.changed_paths:
            revision = self.info.create_revision(identifier, filename.path)
            revision.set_author(log.author)
            revision.set_date(self.parse_date(log.date))
            revision.save()

    def analyze(self, branch="trunk"):
        head = self.get_head_revision()

        while head > 0:
            self.parse(head)

            head = head - 1

    def get_branches(self):
        result = [("Trunk", "/trunk")]

        return result

        for branch, lock in self.repo.list("branches"):
            import pdb; pdb.set_trace()
            result.append(branch, branch.path)

        return result

    def update(self, path):
        if not os.path.exists(path):
            self.repo.checkout(self.info.url, path, revision=Revision(revision_kind.head), recurse=True)
        else:
            self.repo.update(path)

    def folder_is_valid(self, name):
        return not name == ".svn"


class Mercurial(Connector):

    def create_repo(self, repo):
        return hg.Repo(repo)
