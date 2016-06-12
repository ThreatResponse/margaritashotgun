#!/usr/bin/env python

import time
import sys
import logging
from datetime import datetime


class multilogger():

    def __init__(self, logger_name, log_file, desc="action"):
        self.logger = logging.getLogger(logger_name)

        std_logger = False
        for handler in self.logger.handlers:
            if handler.stream.name == '<stdout>' or handler.stream.name == '<stderr>':
                std_logger = True

        if not std_logger:
            streamhandler = logging.StreamHandler(sys.stdout)
            self.logger.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            streamhandler.setFormatter(formatter)
            self.logger.addHandler(streamhandler)

        self.log_file = log_file
        with open(self.log_file, 'w') as f:
            f.write('[\n')
            f.close

        fileHandler = logging.FileHandler(self.log_file, mode='a')
        formatter = logging.Formatter(
            "\t{'timestamp': %(unixtime)s, 'message': '%(message)s', " +
            "desc: '{}', 'datetime': '%(isotime)s'}}".format(desc)
        )
        fileHandler.setFormatter(formatter)
        self.logger.addHandler(fileHandler)

    def info(self, message):
        tm = int(time.time())
        dt = datetime.utcfromtimestamp(tm).isoformat()
        times = {'unixtime': tm, 'isotime': dt}
        self.logger.info(message, extra=times)

    def __del__(self):
        with open(self.log_file, 'a') as f:
            f.write(']')
            f.close()

if __name__=="__main__":
    logger = multilogger('margarita_shotgun', 'test-json.log', desc="jsonlog action")
    logger.info("completed test of json log")
