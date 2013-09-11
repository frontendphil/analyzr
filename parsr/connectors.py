from datetime import datetime
from hashlib import md5
from os import path, walk

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

    def get_file_statistics(self):
        raise NotImplementedError

    def parse_date(self, timestamp):
        return datetime.fromtimestamp(int(timestamp))


class Git(Connector):

    def create_repo(self, repo):
        folder = self.get_repo_path(repo)

        if path.exists(folder):
            return git.Repo(folder)

        return git.Repo.clone_from(repo.url, folder)

    def get_repo_path(self, repo):
        return "%s/%s" % (CHECKOUT_PATH, md5(repo.url).hexdigest())

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

    def get_file_statistics(self, path=None):
        if not path:
            path = self.get_repo_path(self.info)

        for folder, folders, files in walk(path):
            for folder in folders:
                if folder == ".git":
                    continue

                self.get_file_statistics(folder)

            for name in files:
                if name.startswith("."):
                    continue

                mimetype, encoding = guess_type(name)
                self.info.add_mime_info(mimetype)


class SVN(Connector):

    def create_repo(self, repo):
        client = Client()

        client.callback_get_login = self.get_login(repo)
        client.callback_ssl_server_trust_prompt = self.get_trust(repo)
        client.callback_notify = self.get_notify()

        return client

    def get_notify(self):
        def callback_notify(events):
            print events

        return callback_notify

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
        files = self.repo.info2(self.info.url,
            revision=Revision(revision_kind.number, identifier),
            recurse=False)

        for filename, info in files:
            last_changed = info["last_changed_rev"]

            if not last_changed or not last_changed.number == identifier:
                continue

            revision = self.info.create_revision(identifier, filename)
            revision.set_author(info["last_changed_author"])
            revision.set_date(self.parse_date(info["last_changed_date"]))
            revision.save()

    def analyze(self, branch="trunk"):
        head = self.get_head_revision()

        while head > 0:
            self.parse(head)

            head = head - 1

    # TODO: Not working on remote end
    def get_branches(self):
        result = [("Trunk", "/trunk")]

        for branch, lock in self.repo.list("branches"):
            import pdb; pdb.set_trace()
            result.append(branch, branch.path)

        return result


class Mercurial(Connector):

    def create_repo(self, repo):
        return hg.Repo(repo)
