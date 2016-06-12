#!/usr/bin/env python

import sys
import random
import logging
from .cli import cli
from .utility import utility
from .worker import master as multiprocessing_master


class margaritashotgun():

    def __init__(self, interactive=True, logger_name=None):
        self.interactive=interactive
        if logger_name is None:
            self.logger = logging.getLogger('margarita_shotgun')
            streamhandler = logging.StreamHandler(sys.stdout)
            self.logger.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            streamhandler.setFormatter(formatter)
            self.logger.addHandler(streamhandler)
        else:
            self.logger = logging.getLogger(logger_name)

    def set_config(self, config):
        util = utility(logger=self.logger)
        self.config = config
        if util.invalid_config(self.config):
            self.logger.info("config verification failed")
            return False
        else:
            return True

    def run(self):
        if self.interactive:
            c = cli(self.logger)
            self.config = c.parse_args()

        util = utility(logger=self.logger)
        multi_config, workers = util.transform(self.config)

        try:
            master = multiprocessing_master(self.logger, multi_config, workers)
            master.start_workers()
        except KeyboardInterrupt:
            sys.exit()

if __name__ == "__main__":
    ms = margaritashotgun()
    ms.run()
