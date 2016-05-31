#!/usr/bin/env python

import sys
import random
import logging
from . import cli
from . import api
from . import worker


class margaritashotgun():

    def __init__(self):
        self.logger = logging.getLogger('margarita_shotgun')
        streamhandler = logging.StreamHandler(sys.stdout)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        streamhandler.setFormatter(formatter)
        self.logger.addHandler(streamhandler)

    def set_config(self, config):
        a = api.api(logger=self.logger)
        self.config = config
        if a.invalid_config(self.config):
            self.logger.info("config_verify_fail exiting")
            return False
        else:
            return True

    def run(self):
        c = cli.cli(self.logger)
        self.config = c.parse_args()
        mp_config = []

        try:
            workers = self.config['workers']
        except KeyError:
            self.logger.info("no worker count specified. defaulting to 1")
            workers = 1

        for host in self.config['hosts']:
            if workers > 1:
                draw_pbar = False
            else:
                draw_pbar = True

            try:
                aws_config = self.config['aws']
            except KeyError:
                aws_config = False

            if aws_config:
                conf = {'logger': self.logger.name, 'host': host,
                        'aws': self.config['aws'], 'pbar': draw_pbar}
            else:
                conf = {'logger': self.logger.name, 'host': host,
                        'pbar': draw_pbar}
            mp_config.append(conf)
        master = worker.master(self.logger, mp_config, workers)
        master.start_workers()

if __name__ == "__main__":
    ms = margaritashotgun()
    ms.run()
