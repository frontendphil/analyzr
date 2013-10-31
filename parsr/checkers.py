import subprocess
import json

from jinja2 import Environment, FileSystemLoader
from xml.dom import minidom
from decimal import Decimal

from parsr.metrics import Metric

from analyzr.settings import CONFIG_PATH, RESULT_PATH, PROJECT_PATH


class Checker(object):

    def __init__(self, config_path, result_path):
        self.measures = {}
        self.env = Environment(loader=FileSystemLoader(CONFIG_PATH))

        self.config_path = config_path
        self.result_path = result_path

    def config_file(self, revision):
        return "%s/%s.xml" % (self.result_path, revision.identifier)

    def result_file(self, revision):
        return "%s/%s.xml" % (self.result_path, revision.identifier)

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

        filename = self.config_file(revision)
        result_file = self.result_file(revision)

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
            raise Exception("Error running analyzer script")

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

class ComplexityReport(Checker):

    def result_file(self, revision):
        return "%s/%s" % (self.result_path, revision.identifier)

    def configure(self, files, revision, connector):
        self.result = self.result_file(revision)
        self.files = files
        self.base_path = connector.get_repo_path()

    def get_file_path(self, f):
        return "%s/%s" % (self.base_path, f.name)

    def run(self):
        for f in self.files:
            path = self.get_file_path(f)
            result = "%s_%s.json" % (self.result, f.get_identifier())

            returncode = subprocess.call(["cr", "-f", "json", "-o", result, path])

            if not returncode == 0:
                raise Exception("Error running analyzer script")

    def parse(self, connector):
        results = {}

        for f in self.files:
            path = "%s_%s.json" % (self.result, f.get_identifier())

            with open(path) as result:
                data = json.load(result)[0]

                halstead = data["aggregate"]["complexity"]["halstead"]
                mccabe = data["aggregate"]["complexity"]["cyclomatic"]

                results[f.name] = [
                    {
                        "kind": "CyclomaticComplexity",
                        "value": Decimal("%d" % mccabe)
                    },
                    {
                        "kind": "Halstead",
                        "value": {
                            "volume": Decimal("%d" % round(halstead["volume"], 2)),
                            "difficulty": Decimal("%d" % round(halstead["difficulty"], 2)),
                            "effort": Decimal("%d" % round(halstead["effort"], 2))
                        }
                    }
                ]

        return results
