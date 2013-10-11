from parsr.connectors import Connector

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

        cls.analyzers[mimetype] = analyzer

    def __init__(self, repo):
        self.repo = repo
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
            analyzer.measure()

    def start(self):
        for revision in self.repo.revisions():
            self.connector.checkout(revision)
            self.measure(revision)


class BaseAnalyzer(object):

    def __init__(self):
        self.files = []

    def add_file(self, f):
        self.files.append(f)

    def measure(self):
        self.create_configuration()
        self.run()

        self.files = []

    def create_configuration(self):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError


class Java(BaseAnalyzer):
    pass

Analyzer.register("text/x-java-source", Java)


class JavaScript(BaseAnalyzer):
    pass

Analyzer.register("application/javascript", JavaScript)


class C(BaseAnalyzer):
    pass

Analyzer.register("text/x-c", C)
