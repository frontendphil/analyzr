from jinja2 import Environment, FileSystemLoader

from parsr.connectors import Connector

from analyzr.settings import CONFIG_PATH, RESULT_PATH, PROJECT_PATH

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
        self.repo = repo
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
                analyzer.measure(revision, self.connector)

    def start(self):
        import pdb; pdb.set_trace()

        self.connector.switch_to(self.branch)

        for revision in self.repo.revisions():
            self.connector.checkout(revision)
            self.measure(revision)


class BaseAnalyzer(object):

    def __init__(self):
        self.files = []
        self.env = Environment(loader=FileSystemLoader(CONFIG_PATH))

    def add_file(self, f):
        self.files.append(f)

    def measure(self, revision, connector):
        self.create_configuration(revision, connector)
        self.run()
        self.parse_measures()

        self.files = []

    def empty(self):
        return len(self.files) == 0

    def create_configuration(self, revision, connector):
        raise NotImplementedError

    def parse_measures(self):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError


class Java(BaseAnalyzer):

    def create_configuration(self, revision, connector):
        base_path = connector.get_repo_path()

        template = self.env.get_template("pmd.xml")
        ruleset = "%s/pmd.ruleset.xml"
        filename = "%s/%s.xml" % (CONFIG_PATH, revision.identifier)
        target = "%s/%s.xml" % (RESULT_PATH, revision.identifier)

        with open(filename, "wb") as f:
            f.write(template.render({
                "project_path": PROJECT_PATH,
                "base_path": base_path,
                "target": target,
                "ruleset": ruleset,
                "files": self.files,
                "language": "java",
                "version": "1.6"
            }))

Analyzer.register("text/x-java-source", Java)


class JavaScript(BaseAnalyzer):
    pass

Analyzer.register("application/javascript", JavaScript)


class C(BaseAnalyzer):
    pass

Analyzer.register("text/x-c", C)
