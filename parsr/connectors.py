from datetime import datetime
from hashlib import md5

import os
import git
import hgapi as hg

from pysvn import Client, Revision
from pysvn import opt_revision_kind as revision_kind

from analyzr.settings import CHECKOUT_PATH


class Action(object):
    ADD = "A"
    MODIFY = "M"
    MOVE = "C"
    DELETE = "D"


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

    def update(self, path):
        pass

    def parse_date(self, timestamp):
        return datetime.fromtimestamp(int(timestamp))


class Git(Connector):

    def create_repo(self, repo):
        folder = self.get_repo_path(repo)

        if os.path.exists(folder):
            return git.Repo(folder)

        return git.Repo.clone_from(repo.url, folder)

    def create_revision(self, commit, filename, action):
        revision = self.info.create_revision(commit.hexsha, filename, action)
        revision.set_author(commit.author)
        revision.set_date(self.parse_date(commit.committed_date))
        revision.save()

    def parse(self, parent, commit=None):
        if not commit:
            return

        stats = commit.stats

        if not parent:
            for filename, info in stats.files.iteritems():
                self.create_revision(commit, filename, Action.ADD)

            return

        diffs = parent.diff(commit)

        for diff in diffs:
            action = Action.MODIFY
            filename = None

            if diff.new_file:
                action = Action.ADD
                filename = diff.b_blob.path

            if diff.deleted_file:
                action = Action.DELETE

            if diff.renamed:
                action = Action.MOVE
                filename = diff.b_blob.path

            if not filename:
                filename = diff.a_blob.path

            self.create_revision(commit, filename, action)


    def analyze(self, branch="master"):
        last_commit = None

        for commit in self.repo.iter_commits():
            self.parse(commit, last_commit)

            last_commit = commit

        # create initial commit
        self.parse(None, last_commit)

    def get_branches(self):
        result = []

        for info in self.repo.remotes.origin.fetch():
            result.append((info.name, info.ref.path))

        return result


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

    def get_head_revision(self, branch):
        head = self.repo.info2("%s%s" % (self.info.url, branch.path),
            revision=Revision(revision_kind.head),
            recurse=False)

        name, info = head[0]

        revision = info["rev"]

        return revision.number

    def parse(self, branch, identifier):
        log = self.repo.log("%s%s" % (self.info.url, branch.path),
            revision_start=Revision(revision_kind.number, identifier),
            revision_end=Revision(revision_kind.number, identifier),
            discover_changed_paths=True,
            limit=0)

        if len(log) == 0:
            # Revision does not affect current branch

            return

        log = log[0]

        for filename in log.changed_paths:
            revision = self.info.create_revision(identifier, filename.path, filename.action)
            revision.set_author(log.author)
            revision.set_date(self.parse_date(log.date))
            revision.save()

    def analyze(self, branch):
        head = self.get_head_revision(branch)

        while head > 0:
            self.parse(branch, head)

            head = head - 1

    def get_branches(self):
        branches = []

        for folder, lock in self.repo.list(self.info.url, recurse=False, revision=Revision(revision_kind.head)):
            folder_name = folder.path.replace(self.info.url, "")

            if folder_name == "/branches":
                for branch, lock in self.repo.list(folder.path, recurse=False, revision=Revision(revision_kind.head)):
                    directory = branch.path.replace(self.info.url, "")
                    name = directory.replace("/branches/", "")

                    branches.append((name, directory))

            if folder_name == "/trunk":
                branches.append(("Trunk", folder_name))

        if not branches:
            branches.append(("Root", "/"))

        return branches

    def update(self, path):
        if not os.path.exists(path):
            self.repo.checkout(self.info.url, path, revision=Revision(revision_kind.head), recurse=True)
        else:
            self.repo.update(path)


class Mercurial(Connector):

    def create_repo(self, repo):
        return hg.Repo(repo)
