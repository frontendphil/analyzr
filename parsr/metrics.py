class Metric(object):

    metrics = {}

    @classmethod
    def register(cls, key, metric):
        cls.metrics[key] = metric()

    @classmethod
    def get(cls, key):
        if key in cls.metrics:
            return cls.metrics[key]

        return None


class CyclomaticComplexity(object):

    def parse(self, violation):
        return int(violation.attributes["message"].value)

Metric.register("CyclomaticComplexity", CyclomaticComplexity)


class FanIn(object):
    pass


class FanOut(object):

    def parse(self, violation):
        return int(violation.attributes["message"].value)

Metric.register("ClassFanOutComplexity", FanOut)


class Halstead(object):
    pass


class DistanceFromMainSequence(object):
    pass
