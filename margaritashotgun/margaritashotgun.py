#!/usr/bin/env python

import sys
import random
import logging
from . import cli
from . import api
from . import worker


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
        a = api.api(logger=self.logger)
        self.config = config
        if a.invalid_config(self.config):
            self.logger.info("config_verify_fail exiting")
            return False
        else:
            return True

    def run(self):
        c = cli.cli(self.logger)
        if self.interactive:
            self.config = c.parse_args()
        mp_config = []

        try:
            workers = int(self.config['workers'])
        except Exception as e:
            if type(e) == KeyError:
                self.logger.info("no worker count specified. defaulting to 1")
                workers = 1
                pass
            elif type(e) == ValueError:
                if self.config['workers'] != 'auto':
                    self.logger.info("invalid worker config, " +
                                     "workers must be an integer or auto")
                    raise ValueError('workers must be an integer or "auto"')
                else:
                    workers = self.config['workers']
                    pass
            else:
                raise

        try:
            log_dir = self.config['logging']['dir']
            log_prefix = self.config['logging']['prefix']
        except KeyError:
            log_dir = ''
            log_prefix = ''

        for host in self.config['hosts']:
            try:
                aws_config = self.config['aws']
            except KeyError:
                aws_config = False

            if aws_config:
                conf = {'host': host,
                        'aws': aws_config}
            else:
                conf = {'host': host}

            conf['logging'] = {'logger': self.logger.name,
                               'dir': log_dir,
                               'prefix': log_prefix}
            mp_config.append(conf)

        try:
            master = worker.master(self.logger, mp_config, workers)
            master.start_workers()
        except KeyboardInterrupt:
            sys.exit()

if __name__ == "__main__":
    ms = margaritashotgun()
    ms.run()
