from datetime import datetime
from hashlib import md5
from shutil import rmtree

import os
import git
import locale

from mercurial import ui, hg, node

from pysvn import Client, Revision
from pysvn import opt_revision_kind as revision_kind
from pysvn import wc_status_kind as svn_status

from analyzr.settings import CHECKOUT_PATH

# The following code is needed in order for the SVN lib to work
# correctly accross systems. It would otherwise crash if non-standard
# characters are used in file names
language_code, encoding = locale.getdefaultlocale()

if language_code is None:
    language_code = "en_US"

if encoding is None:
    encoding = "UTF-8"

if encoding.lower() == "utf":
    encoding = "UTF-8"

locale.setlocale(locale.LC_ALL, "%s.%s" % (language_code, encoding))


class Action(object):
    ADD = "A"
    MODIFY = "M"
    MOVE = "C"
    DELETE = "D"

    @classmethod
    def readable(cls):
        return [cls.ADD, cls.MODIFY]


class Connector(object):

    connectors = {}

    @classmethod
    def register(cls, kind, connector):
        if kind in cls.connectors:
            raise "Connector already registered"

        cls.connectors[kind] = connector

    @classmethod
    def get(cls, repo):
        kind = repo.kind

        if kind in cls.connectors:
            return cls.connectors[kind](repo)

        return None

    def __init__(self, repo):
        self.info = repo
        self.repo = self.create_repo(repo)

    def create_repo(self, repo):
        raise NotImplementedError

    def analyze(self, branch, resume_at=None):
        raise NotImplementedError

    def checkout(self, revision):
        raise NotImplementedError

    def switch_to(self, branch):
        raise NotImplementedError

    def get_churn(self, revision, filename):
        raise NotImplementedError

    def get_branches(self):
        return [("Root", "/")]

    def repo_id(self):
        return md5(self.info.url).hexdigest()

    def get_repo_path(self):
        return "%s/%s" % (CHECKOUT_PATH, self.repo_id())

    def update(self, path):
        pass

    def lock(self, revision):
        pass

    def unlock(self):
        pass

    def parse_date(self, timestamp):
        return datetime.fromtimestamp(int(timestamp))

    def clear(self):
        path = self.get_repo_path()

        if not os.path.exists(path):
            return

        rmtree(path)


class Git(Connector):

    def get_branch_name(self, branch):
        return branch.name.replace("origin/", "")

    def switch_to(self, branch):
        self.repo.remotes.origin.fetch()

        branch_name = self.get_branch_name(branch)

        for head in self.repo.heads:
            if not head.name == branch_name:
                continue

            self.repo.head.reference = head
            self.repo.head.reset(index=True, working_tree=True)
            self.repo.remote().pull()

            return

        self.repo.git.checkout(branch.name, b=self.get_branch_name(branch))

        self.switch_to(branch)

    def checkout(self, revision):
        self.repo.head.reset(commit=revision.identifier, index=True, working_tree=True)

    def create_repo(self, repo):
        folder = self.get_repo_path()

        if os.path.exists(folder):
            return git.Repo(folder)

        return git.Repo.clone_from(repo.url, folder)

    def lock(self, revision):
        self.commit = self.repo.commit(revision.identifier)

    def unlock(self):
        self.commit = None

    def get_churn(self, revision, filename):
        if not self.commit:
            return

        stats = self.commit.stats.files

        if not filename in stats:
            return

        return {
            "added": stats[filename]["insertions"],
            "removed": stats[filename]["deletions"]
        }

    def parse(self, branch, parent, commit=None):
        if not commit:
            branch.revision_count = parent.count()
            branch.save()

            return

        stats = commit.stats

        revision = branch.create_revision(commit.hexsha)
        revision.set_author(commit.author.name, commit.author.email)
        revision.set_date(self.parse_date(commit.committed_date))

        if not parent:
            for filename, info in stats.files.iteritems():
                revision.add_file(filename, Action.ADD)
                revision.save()

            return revision

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

            revision.add_file(filename, action, original=original)

        revision.save()

        return revision


    def analyze(self, branch, resume_at=None):
        last_commit = None
        last_revision = resume_at.next if resume_at else None

        self.switch_to(branch)

        for commit in self.repo.iter_commits():
            if resume_at and not resume_at.represents(commit.hexsha):
                last_commit = commit

                continue

            if resume_at:
                # this revision is being recreated. so it has to go!
                resume_at.delete()

            revision = self.parse(branch, commit, last_commit)

            if revision:
                revision.next = last_revision
                revision.save()

                last_revision = revision

            last_commit = commit

        # create initial commit
        revision = self.parse(branch, None, last_commit)

        if revision:
            revision.next = last_revision
            revision.save()

    def get_branches(self):
        result = []

        for info in self.repo.remotes.origin.fetch():
            result.append((info.name, info.ref.path))

        return result


Connector.register("git", Git)


class SVN(Connector):

    def is_checked_out(self):
        return os.path.exists(self.get_repo_path())

    def switch_to(self, branch):
        path = "%s%s" % (self.info.url, branch.path)

        if not self.is_checked_out():
            self.repo.checkout(path, self.get_repo_path(), ignore_externals=True)
        else:
            self.repo.switch(self.get_repo_path(), path)

    def checkout(self, revision):
        self.repo.update(self.get_repo_path(),
            recurse=True,
            revision=Revision(revision_kind.number, revision.identifier),
            ignore_externals=True)

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

    def full_path(self, revision, filename):
        branch = revision.branch
        repo = branch.repo

        return "%s/%s/%s" % (repo.url, branch.path, filename)

    def get_churn(self, revision, filename):
        return
        previous = revision.get_previous()

        if not previous:
            return

        summary = self.repo.diff_summarize(
            self.full_path(previous, filename),
            Revision(revision_kind.number, previous.identifier),
            self.full_path(revision, filename),
            Revision(revision_kind.number, revision.identifier),
            ignore_ancestry=True
            )

        added = 0
        removed = 0

        for line in summary:
            if line.startswith("+"):
                added = added + 1

            if line.startswith("-"):
                removed = removed + 1

        return {
            "added": added,
            "removed": removed
        }

    def parse(self, branch, identifier):
        try:
            log = self.repo.log("%s%s" % (self.info.url, branch.path),
                revision_start=Revision(revision_kind.number, identifier),
                revision_end=Revision(revision_kind.number, identifier),
                discover_changed_paths=True,
                limit=0)
        except:
            return

        if len(log) == 0:
            # Revision does not affect current branch
            return

        log = log[0]

        revision = branch.create_revision(identifier)
        revision.set_author(log.author)
        revision.set_date(self.parse_date(log.date))

        for filename in log.changed_paths:
            original = None

            if filename.action == Action.MOVE:
                original = filename.copyfrom_path

            path = filename.path.decode("utf-8").replace("%s/" % branch.path, "")

            revision.add_file(path, filename.action, original=original)

        revision.save()

        return revision

    def get_start_revision(self, resume, head):
        while head > 0:
            if resume and not resume.represents("%d" % head):
                head = head - 1

                continue

            return head

    def analyze(self, branch, resume_at=None):
        head = self.get_head_revision(branch)

        branch.revision_count = head
        branch.save()

        last_revision = None

        if resume_at:
            head = self.get_start_revision(resume_at, head)

            last_revision = resume_at.next

            # this revision is being recreated. so it has to go!
            resume_at.delete()

        while head > 0:
            revision = self.parse(branch, head)

            if revision:
                revision.next = last_revision
                revision.save()

                last_revision = revision

            head = head - 1

    def get_branches(self):
        branches = []

        for folder, lock in self.repo.list(self.info.url, recurse=False, revision=Revision(revision_kind.head)):
            folder_name = folder.path.replace(self.info.url, "")

            if folder_name == "/branches":
                for branch, lock in self.repo.list(folder.path, recurse=False, revision=Revision(revision_kind.head)):
                    directory = branch.path.replace(self.info.url, "")
                    name = directory.replace("/branches/", "")

                    if name == "/branches":
                        continue

                    branches.append((name, directory))

            if folder_name == "/trunk":
                branches.append(("Trunk", folder_name))

        if not branches:
            return super(SVN, self).get_branches()

        return branches

    def update(self, path):
        if not os.path.exists(path):
            self.repo.checkout(self.info.url, path,
                revision=Revision(revision_kind.head),
                recurse=True,
                ignore_externals=True)
        else:
            self.repo.update(path, ignore_externals=True)


Connector.register("svn", SVN)


class Mercurial(Connector):

    def create_repo(self, repo):
        self.ui = ui.ui()

        folder = self.get_repo_path()

        if os.path.exists(folder):
            return hg.repository(self.ui, folder)

        try:
            hg.clone(self.ui, dict(), str(repo.url), folder, pull=True)
        except ValueError:
            repo = hg.repository(self.ui, folder)

            hg.update(repo, node.hex(node.nullid))

        return self.create_repo(repo)

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

    def parse(self, branch, commit):
        revision = branch.create_revision(commit.hex())
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

            revision.add_file(filename, action, original=original)

        revision.save()


    def analyze(self, branch):
        # self.switch_to(branch)

        for id in self.repo:
            commit = self.repo[id]

            self.parse(branch, commit)


Connector.register("mercurial", Mercurial)
