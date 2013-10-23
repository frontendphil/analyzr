import subprocess

from jinja2 import Environment, FileSystemLoader

from xml.dom import minidom

from parsr.metrics import Metric

from analyzr.settings import CONFIG_PATH, RESULT_PATH, PROJECT_PATH


class Checker(object):

    def __init__(self):
        self.measures = {}
        self.env = Environment(loader=FileSystemLoader(CONFIG_PATH))

    def config_file(self, revision, connector):
        return "%s/%s/configs/%s.xml" % (RESULT_PATH, connector.repo_id(), revision.identifier)

    def result_file(self, revision, connector):
        return "%s/%s/results/%s.xml" % (RESULT_PATH, connector.repo_id(), revision.identifier)

    def configure(self, files, revision, connector):
        pass

    def run(self):
        pass

    def parse(self, connector):
        return {}


class Checkstyle(Checker):

    def configure(self, files, revision, connector):
        self.measures = {}

        template = self.env.get_template("checkstyle.xml")

        filename = self.config_file(revision, connector)
        result_file = self.result_file(revision, connector)

        options = {
            "checker": "checkstyle",
            "project_path": PROJECT_PATH,
            "base_path": connector.get_repo_path(),
            "target": result_file,
            "files": files
        }

        with open(filename, "wb") as f:
            f.write(template.render(options))

        self.configuration = filename
        self.results = result_file

        return filename, result_file

    def run(self):
        if not self.configuration:
            return

        returncode = subprocess.call(["ant", "-f", self.configuration, "measure"])

        if not returncode == 0:
            raise "Error running analyzer script"

        # Don't allow multiple runs with the same configuration
        self.configuration = None

    def parse_violation(self, filename, violation):
        source = violation.attributes["source"].value

        kind = source.replace("com.puppycrawl.tools.checkstyle.checks.metrics.", "")\
                     .replace("Check", "")

        metric = Metric.get(kind)

        if not metric:
            return

        value = metric.parse(violation)

        if not filename in self.measures:
            self.measures[filename] = []

        self.measures[filename].append({
            "kind": kind,
            "value": value
        })

    def aggregate_values(self, filename):
        if not filename in self.measures:
            return

        metrics = {}

        for measure in self.measures[filename]:
            if not measure["kind"] in metrics:
                metrics["kind"] = []

            metrics["kind"].append(measure["value"])

        self.measures[filename] = []

        for metric, values in metrics.iteritems():
            self.measures[filename].append({
                "kind": metric,
                "value": sum(values) / len(values)
            })

    def parse(self, connector):
        if not self.results:
            return

        xml_doc = minidom.parse(self.results)
        files = xml_doc.getElementsByTagName("file")

        for f in files:
            # replace leading / as files are internally stored without it.
            name = f.attributes["name"].value.replace(connector.get_repo_path(), "")\
                                             .replace("/", "", 1)

            violations = f.getElementsByTagName("error")

            for violation in violations:
                self.parse_violation(name, violation)

            self.aggregate_values(name)

        # Parse results only once
        self.results = None

        return self.measures

class AOPMetrics(Checker):
    pass
