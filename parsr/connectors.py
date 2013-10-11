from datetime import datetime
from hashlib import md5

import os
import git

from mercurial import ui, hg, node

from pysvn import Client, Revision
from pysvn import opt_revision_kind as revision_kind
from pysvn import wc_status_kind as svn_status

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
        return [("Root", "/")]

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

    def parse(self, parent, commit=None):
        if not commit:
            return

        stats = commit.stats

        revision = self.info.create_revision(commit.hexsha)
        revision.set_author(commit.author)
        revision.set_date(self.parse_date(commit.committed_date))

        if not parent:
            for filename, info in stats.files.iteritems():
                revision.add_file(filename, Action.ADD)
                revision.save()

            return

        diffs = parent.diff(commit)

        for diff in diffs:
            action = Action.MODIFY
            filename = None
            original = None

            if diff.new_file:
                action = Action.ADD
                filename = diff.b_blob.path

            if diff.deleted_file:
                action = Action.DELETE

            if diff.renamed:
                action = Action.MOVE

                filename = diff.b_blob.path
                original = diff.a_blob.path

            if not filename:
                filename = diff.a_blob.path

            revision.add_file(filename, action, original)

        revision.save()


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

    def get_action(self, status):
        if status == svn_status.added:
            return Action.ADD

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

        revision = self.info.create_revision(identifier)
        revision.set_author(log.author)
        revision.set_date(self.parse_date(log.date))

        for filename in log.changed_paths:
            original = None

            if filename.action == Action.MOVE:
                original = filename.copyfrom_path

            revision.add_file(filename.path, filename.action, original)

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
            return super(SVN, self).get_branches()

        return branches

    def update(self, path):
        if not os.path.exists(path):
            self.repo.checkout(self.info.url, path, revision=Revision(revision_kind.head), recurse=True)
        else:
            self.repo.update(path)


class Mercurial(Connector):

    def create_repo(self, repo):
        self.ui = ui.ui()

        folder = self.get_repo_path(repo)

        if os.path.exists(folder):
            return hg.repository(self.ui, folder)

        try:
            hg.clone(self.ui, dict(), str(repo.url), folder, pull=True)
        except ValueError:
            repo = hg.repository(self.ui, folder)

            hg.update(repo, node.hex(node.nullid))

        return self.create_repo()

    def get_action(self, filectx):
        if filectx.renamed():
            return Action.MOVE

        try:
            filectx.p1()
        except IndexError:
            return Action.ADD

        try:
            filectx.p2()
        except IndexError:
            return Action.DELETE

        return Action.MODIFY

    def get_original(self, filectx):
        peer = filectx.p1()

        return peer.path()

    def parse(self, commit):
        revision = self.info.create_revision(commit.hex())
        revision.set_author(commit.user())

        timestamp, foo = commit.date()

        revision.set_date(self.parse_date(timestamp))

        for filename in commit.files():
            action = None

            try:
                filectx = commit.filectx(filename)
                action = self.get_action(filectx)
            except:
                action = Action.DELETE

            original = None

            if action == Action.MOVE:
                original = self.get_original(filectx)

            revision.add_file(filename, action, original)

        revision.save()


    def analyze(self, branch):
        for id in self.repo:
            commit = self.repo[id]

            self.parse(commit)
