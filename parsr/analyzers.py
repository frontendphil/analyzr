import os
import shutil

import pysvn

from parsr.connectors import Connector
from parsr.checkers import JHawk, ComplexityReport

from analyzr.settings import RESULT_PATH


class AnalyzeError(Exception):

    def __init__(self, error, revision, f):
        self.error = error
        self.revision = revision
        self.f = f

        super(AnalyzeError, self).__init__()

    def __str__(self):
        return "%s\n\caused by revision\n\n%s\n\nprocessing file\n\n%s" % (
            self.error,
            self.revision,
            self.f
        )

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.__unicode__()


class Analyzer(object):

    analyzers = {}

    @classmethod
    def parseable_types(cls):
        types = []

        for key, value in cls.analyzers.iteritems():
            types.append(key)

        return types

    @classmethod
    def register(cls, mimetype, checker):
        if not mimetype in cls.analyzers:
            cls.analyzers[mimetype] = []

        cls.analyzers[mimetype].append(BaseAnalyzer(checker))

    def __init__(self, repo, branch):
        self.branch = branch
        self.connector = Connector.get(repo)

    def get_specific_analyzers(self, mimetype):
        if not mimetype in Analyzer.analyzers:
            return []

        return Analyzer.analyzers[mimetype]

    def cleanup(self):
        for mimetype, analyzers in self.analyzers.iteritems():
            [analyzer.clear() for analyzer in analyzers]

    def measure(self, revision):
        self.cleanup()

        for f in revision.modified_files():
            for analyzer in self.get_specific_analyzers(f.mimetype):
                analyzer.add_file(f)

        for mimetype, analyzers in self.analyzers.iteritems():
            for analyzer in analyzers:
                if not analyzer.empty():
                    results = analyzer.measure(revision, self.connector)

                    self.store_results(revision, results)

    def store_results(self, revision, results):
        self.connector.lock(revision)

        for filename, measures in results.iteritems():
            try:
                f = revision.get_file(filename)
                f.add_measures(measures)

                code_churn = self.connector.get_churn(revision, f.full_path())

                f.add_churn(code_churn)
            except Exception, e:
                self.connector.unlock()

                raise AnalyzeError(e, revision, f)

        self.connector.unlock()

    def start(self, revision=None):
        self.connector.switch_to(self.branch)

        if not revision:
            revision = self.branch.first_revision()

        while revision:
            try:
                self.connector.checkout(revision)
                self.measure(revision)
            except pysvn.ClientError:
                # happens if branch structure is fucked up
                pass

            revision.measured = True
            revision.save()

            revision = revision.next


class BaseAnalyzer(object):

    def __init__(self, checker):
        self.files = []
        self.checker = checker

    def __str__(self):
        return self.__unicode__()

    def add_file(self, f):
        self.files.append(f)

    def setup_paths(self, connector):
        config_path = "%s/%s/configs" % (RESULT_PATH, connector.repo_id())
        result_path = "%s/%s/results" % (RESULT_PATH, connector.repo_id())

        if not os.path.exists(config_path):
            os.makedirs(config_path)

        if not os.path.exists(result_path):
            os.makedirs(result_path)

        return (config_path, result_path)

    def cleanup(self, config_path, result_path):
        shutil.rmtree(config_path)
        shutil.rmtree(result_path)

        self.clear()

    def clear(self):
        self.files = []

    def measure(self, revision, connector):
        config_path, result_path = self.setup_paths(connector)

        checker = self.checker(config_path, result_path)
        checker.configure(self.files, revision, connector)

        results = None

        if checker.run():
            results = checker.parse(connector)

        self.cleanup(config_path, result_path)

        return results

    def empty(self):
        return len(self.files) == 0


Analyzer.register("x-java-source", JHawk)
Analyzer.register("x-java", JHawk)
Analyzer.register("javascript", ComplexityReport)
