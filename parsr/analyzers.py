import os
import shutil

from parsr.connectors import Connector
from parsr.checkers import JHawk, ComplexityReport

from analyzr.settings import RESULT_PATH

class Analyzer(object):

    analyzers = {}

    @classmethod
    def parseable_types(cls):
        types = []

        for key, value in cls.analyzers.iteritems():
            types.append(key)

        return types

    @classmethod
    def register(cls, mimetype, analyzer):
        if mimetype in cls.analyzers:
            raise "Analyzer already registered"

        cls.analyzers[mimetype] = analyzer()

    def __init__(self, repo, branch):
        self.branch = branch
        self.connector = Connector.get(repo)

    def get_specific_analyzer(self, mimetype):
        if not mimetype in Analyzer.analyzers:
            return None

        return Analyzer.analyzers[mimetype]

    def measure(self, revision):
        for f in revision.modified_files():
            analyzer = self.get_specific_analyzer(f.mimetype)

            if not analyzer:
                continue

            analyzer.add_file(f)

        for mimetype, analyzer in self.analyzers.iteritems():
            if not analyzer.empty():
                results = analyzer.measure(revision, self.connector)

                self.store_results(revision, results)

    def store_results(self, revision, results):
        for filename, measures in results.iteritems():
            f = revision.get_file(filename)
            f.add_measures(measures)

            code_churn = self.connector.get_churn(revision.identifier, filename)

            f.add_churn(code_churn)

    def start(self):
        try:
            self.connector.switch_to(self.branch)
        except:
            pass

        for revision in self.branch.revisions():
            self.connector.checkout(revision)
            self.measure(revision)


class BaseAnalyzer(object):

    def __init__(self):
        self.files = []
        self.results = {}

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
        return

        shutil.rmtree(config_path)
        shutil.rmtree(result_path)

    def measure(self, revision, connector):
        config_path, result_path = self.setup_paths(connector)

        for cls in self.checkers:
            checker = cls(config_path, result_path)
            checker.configure(self.files, revision, connector)
            checker.run()

            results = checker.parse(connector)

            self.store_results(results)

        results = self.results

        self.files = []
        self.results = {}

        self.cleanup(config_path, result_path)

        return results

    def empty(self):
        return len(self.files) == 0

    def store_results(self, results):
        for filename, measures in results.iteritems():
            if not filename in self.results:
                self.results[filename] = []

            self.results[filename] += measures


class Java(BaseAnalyzer):

    def __init__(self):
        self.checkers = [JHawk]

        super(Java, self).__init__()


Analyzer.register("x-java-source", Java)


class JavaScript(BaseAnalyzer):
    def __init__(self):
        self.checkers = [ComplexityReport]

        super(JavaScript, self).__init__()


Analyzer.register("javascript", JavaScript)


class C(BaseAnalyzer):
    pass

Analyzer.register("x-c", C)
