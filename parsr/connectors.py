import git
import hgapi as hg

from pysvn import Client, Revision
from pysvn import opt_revision_kind as revision_kind

from analyzr.settings import SVN_USER_NAME, SVN_PASSWORD

class Connector(object):

    def __init__(self, repo):
        self.repo = self.create_repo(repo)

    def create_repo(self, repo):
        raise NotImplementedError

    def revision_count(self):
        raise NotImplementedError

    def all_authors(self):
        raise NotImplementedError


class Git(Connector):

    def create_repo(self, repo):
        return git.Repo(repo)

    def revision_count(self):
        def count(current):
            revs = 0

            while(True):
                if current.parents:
                    current = current.parents[0]

                    revs = revs + 1
                else:
                    break

            return revs

        return count(self.repo.head.commit)

    def all_authors(self):
        def count(current):
            authors = []

            while(True):
                author = current.author

                if not author in authors:
                    authors.append(author)

                if current.parents:
                    current = current.parents[0]
                else:
                    break

            return authors

        return count(self.repo.head.commit)


class SVN(Connector):

    def __init__(self, repo):
        self.client = Client()

        self.client.callback_get_login = self.get_login

        super(SVN, self).__init__(repo)

    def create_repo(self, repo):
        return repo

    def get_login(realm, username, may_save):
        return True, SVN_USER_NAME, SVN_PASSWORD, False

    def revision_count(self):
        head = self.client.svnpropget("revision", self.repo)

        return head


class Mercurial(Connector):

    def create_repo(self, repo):
        return hg.Repo(repo)
