from django.conf import settings


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Logger:
    __metaclass__ = Singleton

    def __init__(self):
        self.log_file = open(settings.USER_LOG_FILE, 'a')

    def info(self, m):
        self.log("INFO: {}".format(m))

    def warn(self, m):
        self.log("WARN: {}".format(m))

    def error(self, m):
        self.log("ERROR: {}".format(m))

    def log(self, message):
        self.log_file.write(message + "\n")

    def __del__(self):
        self.log_file.close()
