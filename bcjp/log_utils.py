import logging
from datetime import datetime
from django.conf import settings

class LogUtils():
    def __init__(self):
        pass

    def error(self, log, module, source, error):
        try:
            logging.getLogger(log).error("{} [{}] {}:{} => {}".format(datetime.now(), settings.BUILD, module, source, repr(error)))
        except Exception, e:
            pass

    def info(self, log, module, source, message):
        try:
            logging.getLogger(log).info("{} [{}] {}:{} => {}".format(datetime.now(), settings.BUILD, module, source, repr(message)))
        except Exception, e:
            pass