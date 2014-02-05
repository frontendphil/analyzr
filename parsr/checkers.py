import subprocess
import json
import math
import re

import lizard

from jinja2 import Environment, FileSystemLoader
from xml.dom import minidom
from decimal import Decimal

from analyzr.settings import CONFIG_PATH, PROJECT_PATH, LAMBDA

XML_ILLEGAL = u'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])|([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])'
RE_XML_ILLEGAL = XML_ILLEGAL % (
    unichr(0xd800),
    unichr(0xdbff),
    unichr(0xdc00),
    unichr(0xdfff),
    unichr(0xd800),
    unichr(0xdbff),
    unichr(0xdc00),
    unichr(0xdfff),
    unichr(0xd800),
    unichr(0xdbff),
    unichr(0xdc00),
    unichr(0xdfff)
)


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
        return Decimal("%s" % round(float(value), 2))

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
            "sloc_absolute": 0,
            "sloc": 0
        }

    def set(self, filename, key, value):
        if not filename in self.measures:
            self.measures[filename] = self.stub()

        self.measures[filename][key] = self.get_decimal(value)

    def get_value_in_range(self, value, low, high):
        high = high * 1.0
        low = low * 1.0

        if value <= low:
            return 3.0

        if value >= high:
            return 0.0

        return 3.0 - 3.0 * (value / high)

    def squale(self, marks):
        sum_marks = math.fsum([math.pow(LAMBDA, -1.0 * mark) for mark in marks])

        return -1.0 * math.log(sum_marks / (1.0 * len(marks)), LAMBDA)

    def get_hv_mark(self, value):
        return self.get_value_in_range(value, 20, 1000)

    def get_hd_mark(self, value):
        return self.get_value_in_range(value, 10, 50)

    def get_cc_mark(self, value):
        if value <= 2:
            return 3.0

        if value >= 20:
            return 0.0

        return math.pow(2, (7 - value) / 3.5)

    def get_sloc_mark(self, value):
        if value <= 37:
            return 3.0

        if value >= 162:
            return 0.0

        return math.pow(2, (70 - value) / 21.0)

    def get_fan_in_mark(self, value):
        if value <= 19:
            return 3.0

        if value >= 60:
            return 0.0

        return math.pow(2, (30 - value) / 7.0)

    def get_fan_out_mark(self, value):
        if value <= 6:
            return 3.0

        if value >= 19:
            return 0.0

        return math.pow(2, (10 - value) / 2.0)

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
                "filepattern": "|".join(["%s" % f.full_path() for f in chunk])
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

    def get_number(self, parent, node_name):
        return float(self.get_node_value(parent, node_name))

    def get_name(self, parent):
        return self.get_node_value(parent, "Name")

    def get_sloc_squale(self, methods):
        marks = []

        for method in methods:
            metrics = self.get_metrics(method)

            marks.append(self.get_sloc_mark(self.get_number(metrics, "loc")))

        return self.squale(marks)

    def get_hv_squale(self, methods):
        marks = []

        for method in methods:
            metrics = self.get_metrics(method)

            marks.append(self.get_hv_mark(self.get_number(metrics, "halsteadVolume")))

        return self.squale(marks)

    def add_halstead_metrics(self, filename, methods):
        marks = []

        for method in methods:
            metrics = self.get_metrics(method)

            volume = self.get_number(metrics, "halsteadVolume")
            effort = self.get_number(metrics, "halsteadEffort")

            difficulty = effort / volume

            marks.append(self.get_hd_mark(difficulty))

        self.set(filename, "halstead_difficulty", self.squale(marks))
        self.set(filename, "halstead_volume", self.get_hv_squale(methods))

    def get_cc_squale(self, methods):
        marks = []

        for method in methods:
            metrics = self.get_metrics(method)

            marks.append(self.get_cc_mark(self.get_number(metrics, "cyclomaticComplexity")))

        return self.squale(marks)


    def parse(self, connector):
        for result in self.results:
            with open("%s.xml" % result, "r") as f:
                content = f.read()

            content = re.sub(RE_XML_ILLEGAL, "?", content)
            xml_doc = minidom.parseString(content.encode("utf-8"))
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
                        continue

                    methods = cls.getElementsByTagName("Method")

                    if len(methods) == 0:
                        continue

                    self.add_halstead_metrics(filename, methods)

                    self.set(filename, "cyclomatic_complexity", self.get_cc_squale(methods))
                    self.set(filename, "sloc", self.get_sloc_squale(methods))
                    self.set(filename, "sloc_absolute", self.get_node_value(class_metrics, "loc"))

                    fan_in = self.get_number(class_metrics, "fanIn")
                    fan_out = self.get_number(class_metrics, "fanOut")

                    self.set(filename, "fan_in", self.get_fan_in_mark(fan_in))
                    self.set(filename, "fan_out", self.get_fan_out_mark(fan_out))

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

    def get_cc_squale(self, functions):
        # cc = sum([function["cyclomatic"] for function in functions])
        # nom = len(functions)

        # if cc >= 80:
        #     exponent = (30.0 - nom) / 10.0

        #     return pow(2, exponent)

        # if cc < 80 and cc >= 50 and nom >= 15:
        #     return 2 + ((20 - nom) / 30)

        # if cc < 50 and cc >= 30 and nom >= 15:
        #     return 3 + ((15 - nom) / 15)

        # return 3
        marks = []

        for function in functions:
            marks.append(self.get_cc_mark(function["cyclomatic"]))

        return self.squale(marks)

    def get_hv_squale(self, functions):
        marks = []

        for function in functions:
            marks.append(self.get_hv_mark(function["halstead"]["volume"]))

        return self.squale(marks)

    def get_hd_squale(self, functions):
        marks = []

        for function in functions:
            marks.append(self.get_hd_mark(function["halstead"]["difficulty"]))

        return self.squale(marks)

    def get_sloc_squale(self, functions):
        marks = []

        for function in functions:
            marks.append(self.get_sloc_mark(function["sloc"]["logical"]))

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

                functions = data["functions"]

                self.set(filename, "cyclomatic_complexity", self.get_cc_squale(functions))
                self.set(filename, "halstead_volume", self.get_hv_squale(functions))
                self.set(filename, "halstead_difficulty", self.get_hd_squale(functions))
                self.set(filename, "sloc", self.get_sloc_squale(functions))
                self.set(filename, "sloc_absolute", data["aggregate"]["sloc"]["logical"])

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
