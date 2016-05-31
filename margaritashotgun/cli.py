#!/usr/bin/env python

import argparse
import yaml
from . import server
from . import tunnel
from . import memory


class cli():

    def __init__(self, logger):
        self.logger = logger

    def parse_args(self):
        parser = argparse.ArgumentParser(
            description='Remote memory aquisition wrapper for LiME')
        parser.add_argument('-P', '--port', help='ssh port on remote server')
        parser.add_argument('-u', '--username',
                            help='username for ssh connection')
        parser.add_argument('-p', '--password',
                            help='password for user or encrypted keyfile')
        parser.add_argument('-k', '--keyfile',
                            help='path to rsa key for ssh connection')
        parser.add_argument('-m', '--module',
                            help='path to kernel lime kernel module')

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-c', '--config', help='path to config.yml')
        group.add_argument('-s', '--server',
                           help='hostname or ip of target server')

        arguments = parser.parse_args()

        if arguments.keyfile:
            if self.verify_file_path(arguments.keyfile) is False:
                self.logger.info("Invalid private key path: {0}".format(
                                 arguments.keyfile))
                quit()

        if arguments.config is None:
            # TODO: (joel) check default location for creds
            # TODO  (joel) specify bucket + creds file + cred pair with flags
            config = {'aws': {'bucket': None, 'key': None, 'secret': None},
                      'hosts': [{'addr':     arguments.server,
                                 'port':     arguments.port,
                                 'username': arguments.username,
                                 'password': arguments.password,
                                 'keyfile':  arguments.keyfile,
                                 'module':   arguments.module}],
                      'workers': 1}
        else:
            try:
                with open(arguments.config, 'r') as stream:
                    try:
                        config = yaml.load(stream)
                    except yaml.YAMLError as ex:
                        self.logger.info('Invalid config format: {0}'.format(
                                         ex))
                        quit()
            except IOError as ex:
                self.logger.info('Invalid config path: {0}'.format(
                                 arguments.config_file))
                quit()

        return config

    def verify_file_path(self, path):
        if os.path.exists(path):
            return True
        else:
            return False
