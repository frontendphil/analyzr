import os
import subprocess

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

    def setup_paths(self):
        if not os.path.exists(RESULT_PATH):
            os.makedirs("%s/configs" % RESULT_PATH)
            os.makedirs("%s/results" % RESULT_PATH)

    def measure(self, revision, connector):
        self.setup_paths()

        config = self.create_configuration(revision, connector)
        self.run(config)
        self.parse_measures()

        self.files = []

    def config_file(self, revision, connector):
        return "%s/%s/configs/%s.xml" % (RESULT_PATH, connector.repo_id(), revision.identifier)

    def result_file(self, revision, connector):
        return "%s/%s/results/%s.xml" % (RESULT_PATH, connector.repo_id(), revision.identifier)

    def empty(self):
        return len(self.files) == 0

    def create_configuration(self, revision, connector, options={}):
        template = self.env.get_template(self.template)

        filename = self.config_file(revision, connector)

        options["project_path"] = PROJECT_PATH
        options["base_path"] = connector.get_repo_path()
        options["target"] = self.result_file(revision, connector)
        options["files"] = self.files

        with open(filename, "wb") as f:
            f.write(template.render(options))

        return filename

    def parse_measures(self):
        raise NotImplementedError

    def run(self, filename):
        raise NotImplementedError


class Java(BaseAnalyzer):

    def __init__(self):
        self.template = "pmd.xml"

        super(Java, self).__init__()

    def create_configuration(self, revision, connector):
        ruleset = "%s/pmd.ruleset.xml" % CONFIG_PATH

        return super(Java, self).create_configuration(revision, connector, {
            "ruleset": ruleset,
            "language": "java",
            "version": "1.6"
        })

    def run(self, filename):
        subprocess.call(["ant", "-f", filename, "pmd"])

    def parse_measures(self):
        pass

Analyzer.register("text/x-java-source", Java)


class JavaScript(BaseAnalyzer):
    pass

Analyzer.register("application/javascript", JavaScript)


class C(BaseAnalyzer):
    pass

Analyzer.register("text/x-c", C)
