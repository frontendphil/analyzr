import subprocess
import json
import math
import re

import lizard

from jinja2 import Environment, FileSystemLoader
from xml.dom import minidom
from decimal import Decimal

from analyzr.settings import CONFIG_PATH, PROJECT_PATH, LAMBDA


class CheckerException(Exception):

    def __init__(self, checker, cmd, stdout="", stderr=""):
        self.checker = checker
        self.cmd = cmd

        self.stdout = stdout
        self.stderr = stderr

        super(CheckerException, self).__init__()

    def __str__(self):
        value = "STDOUT:\n%s\n\nSTDERR:\n%s" % (self.stdout, self.stderr)

        return "%s raised an error while running command:\n\n%s\n\n%s" % (
            self.checker,
            " ".join(self.cmd),
            value
        )

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.__unicode__()


class Checker(object):

    def __init__(self, config_path, result_path):
        self.measures = {}
        self.env = Environment(loader=FileSystemLoader(CONFIG_PATH))

        self.config_path = config_path
        self.result_path = result_path

        self.files = []

    def __str__(self):
        return self.__unicode__()

    def includes(self, filename):
        for f in self.files:
            if f.endswith(filename):
                return True

        return False

    def get_decimal(self, value):
        return Decimal("%d" % round(float(value), 2))

    def execute(self, cmd):
        # close_fds must be true as python would otherwise reuse created
        # file handles. this would cause a serious memory leak.
        # btw: the file handles are craeted because we pipe stdout and
        # stderr to them.
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)

        stdout, stderr = proc.communicate()

        if not proc.returncode == 0:
            raise CheckerException(self, cmd, stdout=stdout, stderr=stderr)

        return stdout

    def stub(self):
        return {
            "cyclomatic_complexity": 0,
            "halstead_volume": 0,
            "halstead_difficulty": 0,
            "fan_in": 0,
            "fan_out": 0,
            "sloc": 0
        }

    def set(self, filename, key, value):
        if not filename in self.measures:
            self.measures[filename] = self.stub()

        self.measures[filename][key] = self.get_decimal(value)

    def squale(self, marks):
        sum_marks = sum([pow(LAMBDA, -1 * mark) for mark in marks])

        return -1 * math.log(sum_marks / len(marks), LAMBDA)

    def configure(self, files, revision, connector):
        for f in files:
            self.files.append(f.full_path())

    def run(self):
        pass

    def parse(self, connector):
        return {}


class JHawk(Checker):

    # determines how many files are analyzed at once
    # thi sis important as for revisions with a lot of files the
    # generated report might not fit into main memory or can't
    # be parsed.
    FILE_BATCH_SIZE = 50

    def __init__(self, config_path, result_path):
        super(JHawk, self).__init__(config_path, result_path)

        self.name = "jhawk"
        self.files = []
        self.configurations = []
        self.results = []

    def config_file(self, revision, part):
        return "%s/%s_%d.xml" % (self.config_path, revision.identifier, part)

    def result_file(self, revision, part):
        return "%s/%s_%d" % (self.result_path, revision.identifier, part)

    def configure(self, files, revision, connector):
        super(JHawk, self).configure(files, revision, connector)

        self.measures = {}
        self.configurations = []
        self.results = []

        template = self.env.get_template("%s.xml" % self.name)

        file_count = len(files)
        chunks = int(math.ceil(file_count / self.FILE_BATCH_SIZE))

        if not file_count % self.FILE_BATCH_SIZE == 0:
            chunks = chunks + 1

        for i in range(chunks):
            start = i * self.FILE_BATCH_SIZE
            end = min((i + 1) * self.FILE_BATCH_SIZE, file_count)

            chunk = files[start:end]

            filename = self.config_file(revision, i)
            result_file = self.result_file(revision, i)

            options = {
                "checker": self.name,
                "project_path": PROJECT_PATH,
                "base_path": connector.get_repo_path(),
                "target": result_file,
                "filepattern": "|".join([".*/%s" % f.name for f in chunk])
            }

            with open(filename, "wb") as f:
                f.write(template.render(options))

            self.configurations.append(filename)
            self.results.append(result_file)

        self.revision = revision

    def run(self):
        for configuration in self.configurations:
            cmd = [
                "ant",
                "-lib", "%s/lib/%s/JHawkCommandLine.jar" % (PROJECT_PATH, self.name),
                "-f", configuration
            ]

            self.execute(cmd)

        # Don't allow multiple runs with the same configuration
        self.configurations = []

        return True

    def get_metrics(self, parent):
        for node in parent.childNodes:
            if node.localName == "Metrics":
                return node

    def get_node_value(self, parent, node_name):
        for node in parent.childNodes:
            if node.localName == node_name:
                return node.firstChild.nodeValue

    def get_name(self, parent):
        return self.get_node_value(parent, "Name")

    def add_halstead_metrics(self, filename, metrics):
        volume = self.get_node_value(metrics, "halsteadCumulativeVolume")
        effort = self.get_node_value(metrics, "halsteadEffort")
        difficulty = self.get_decimal(effort) / self.get_decimal(volume)

        self.set(filename, "halstead_difficulty", difficulty)
        self.set(filename, "halstead_volume", volume)

    def parse(self, connector):
        for result in self.results:
            xml_doc = minidom.parse("%s.xml" % result)
            packages = xml_doc.getElementsByTagName("Package")

            for package in packages:
                name = self.get_name(package)
                classes = package.getElementsByTagName("Class")

                path = name.replace(".", "/")

                for cls in classes:
                    class_metrics = self.get_metrics(cls)
                    class_name = self.get_node_value(cls, "ClassName")

                    if "$" in class_name:
                        # private class inside of class
                        # ignore!
                        continue

                    filename = "%s/%s.java" % (path, class_name)

                    if not self.includes(filename):
                        # JHawk analyzes _everything_ therefore we must
                        # filter files, which are not present in the current revision
                        continue

                    self.add_halstead_metrics(filename, class_metrics)

                    self.set(filename, "cyclomatic_complexity", self.get_node_value(class_metrics, "avcc"))
                    self.set(filename, "fan_in", self.get_node_value(class_metrics, "fanIn"))
                    self.set(filename, "fan_out", self.get_node_value(class_metrics, "fanOut"))
                    self.set(filename, "sloc", self.get_node_value(class_metrics, "loc"))

        return self.measures

    def __unicode__(self):
        return "JHawk Java Checker"


class ComplexityReport(Checker):

    def __init__(self, config_path, result_path):
        super(ComplexityReport, self).__init__(config_path, result_path)

        self.files = []

    def __unicode__(self):
        return "Complexity Report JavaScript Checker"

    def result_file(self, revision):
        return "%s/%s" % (self.result_path, revision.identifier)

    def configure(self, files, revision, connector):
        self.result = self.result_file(revision)
        self.files = files
        self.base_path = connector.get_repo_path()

    def get_file_path(self, f):
        return "%s/%s" % (self.base_path, f.full_path())

    def run(self):
        for f in self.files:
            path = self.get_file_path(f)
            result = "%s_%s.json" % (self.result, f.get_identifier())

            cmd = ["cr", "-f", "json", "-o", result, path]

            try:
                self.execute(cmd)
            except CheckerException, e:
                if not e.stdout.startswith("Fatal error") and not e.stderr.startswith("Fatal error"):
                    raise e

                # Ignore syntax errors in checked files
                return False

        return True

    # Balmas F, Bellingard F, Denier S, Ducasse S, Franchet B, Laval J, Mordal-Manet K, Vaillergues P. The Squale quality
    # model. Technical Report, INRIA, 2010.
    def get_cc_mark(self, sloc, functions):
        cc = sum([function["cyclomatic"] for function in functions])
        nom = len(functions)

        if cc >= 80:
            exponent = (30.0 - nom) / 10.0

            return pow(2, exponent)

        if cc < 80 and cc >= 50 and nom >= 15:
            return 2 + ((20 - nom) / 30)

        if cc < 50 and cc >= 30 and nom >= 15:
            return 3 + ((15 - nom) / 15)

        return 3

    def get_value_in_range(self, value, low, high):
        if value <= low:
            return 1

        if value >= high:
            return 3

        return 1 + 2 * (value / high)

    def get_hv_mark(self, function):
        value = function["halstead"]["volume"]

        return self.get_value_in_range(value, 20, 1000)

    def get_hv_squale(self, functions):
        marks = []

        for function in functions:
            marks.append(self.get_hv_mark(function))

        return self.squale(marks)

    def get_hd_mark(self, function):
        value = function["halstead"]["difficulty"]

        return self.get_value_in_range(value, 10, 50)

    def get_hd_squale(self, functions):
        marks = []

        for function in functions:
            marks.append(self.get_hd_mark(function))

        return self.squale(marks)

    def get_sloc_squale(self, functions):
        marks = []

        for function in functions:
            # 30 is the threshold for good methods
            marks.append(pow(2, (30 - function["sloc"]["logical"]) / 21))

        return self.squale(marks)

    def parse(self, connector):
        for f in self.files:
            path = "%s_%s.json" % (self.result, f.get_identifier())

            with open(path) as result:
                contents = json.load(result)

                if not contents or not "reports" in contents or not contents["reports"]:
                    continue

                data = contents["reports"][0]

                if len(data["functions"]) == 0:
                    continue

                filename = f.full_path()

                sloc = data["aggregate"]["sloc"]["logical"]
                functions = data["functions"]

                self.set(filename, "cyclomatic_complexity", self.get_cc_mark(sloc, functions))
                self.set(filename, "halstead_volume", self.get_hv_squale(functions))
                self.set(filename, "halstead_difficulty", self.get_hd_squale(functions))
                self.set(filename, "sloc", self.get_sloc_squale(functions))

        return self.measures

class CMetrics(Checker):

    def __init__(self, config_path, result_path):
        self.packages = []
        self.results = {}

        self.re = re.compile("\s{2,}")

        super(CMetrics, self).__init__(config_path, result_path)

    def configure(self, files, revision, connector):
        super(CMetrics, self).configure(files, revision, connector)

        self.repo_path = connector.get_repo_path()

        packages = []

        for f in files:
            if not f.pkg in self.packages:
                packages.append(f.pkg)

        packages = sorted(packages, key=lambda pkg: pkg.left)
        pivot = packages[0]

        self.packages.append(pivot)

        # reduce packages to most common parents
        # this will reduce not needed parses
        for pkg in packages:
            if pkg.left > pivot.left and pkg.left < pivot.right:
                continue

            self.packages.append(pkg)
            pivot = pkg

    def run(self):
        for pkg in self.packages:
            cmd = ["cmetrics", "%s/%s" % (self.repo_path, pkg.name)]

            self.results[pkg.name] = self.execute(cmd)

        return True

    def parse_result(self, data):
        result = {}

        lines = data.split("\n")
        keys = self.re.split(lines.pop(0))

        line = lines.pop(0)

        while line:
            values = self.re.split(line)
            entry = {}

            f = values.pop(0)

            for index, value in enumerate(values):
                entry[keys[index + 1]] = self.get_decimal(value)

            result[f] = entry

            line = lines.pop(0)

        return result

    def parse(self, connector):
        for pkg, data in self.results.iteritems():
            results = self.parse_result(data)

            for f, result in results.iteritems():
                filename = "%s/%s" % (pkg, f)

                if not self.includes(filename):
                    continue

                self.set(filename, "cyclomatic_complexity", result["MEDCY"])
                self.set(filename, "halstead_volume", result["H VOL"])
                self.set(filename, "sloc", result["SLOC"])

        return self.measures

class Lizard(Checker):

    def __init__(self, config_path, result_path):
        self.files = []

        super(Lizard, self).__init__(config_path, result_path)

    def configure(self, files, revision, connector):
        self.files = files
        self.path = connector.get_repo_path()

    def run(self):
        for f in self.files:
            result = lizard.analyze_file("%s/%s" % (self.path, f.full_path()))

            self.set(f.full_path(), "sloc", result.nloc)
            self.set(f.full_path(), "cyclomatic_complexity", result.average_CCN)

    def average(self, functions):
        if len(functions) == 0:
            return 0

        return sum([function.cyclomatic_complexity for function in functions]) / len(functions)

    def parse(self, connector):
        return self.measures
