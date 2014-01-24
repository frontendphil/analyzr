class Classify(object):

    CLASSES = {
        "frontend": [
            "x-javascript"
        ],
        "backend": [
            "x-java-source",
            "x-java"
        ]
    }

    @classmethod
    def frontend(cls):
        return cls.CLASSES["frontend"]

    @classmethod
    def backend(cls):
        return cls.CLASSES["backend"]

    @classmethod
    def all(cls):
        return cls.CLASSES["frontend"] + cls.CLASSES["backend"]
