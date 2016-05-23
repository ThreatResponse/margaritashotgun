#!/usr/bin/env python

import sys
import random
import logging
from . import cli
from . import api


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
        a = api(logger=self.logger)
        self.config = config
        if a.invalid_config(self.config):
            self.logger.info("config_verify_fail exiting")
            return False
        else:
            return True

    def run(self):
        try:
            c = cli.cli(self.logger)
            a = api.api(self.logger)
            self.config = c.parse_args()
            self.remotes = []
            self.tunnels = []
            if a.invalid_config(self.config):
                self.logger.info("config_verify_fail exiting")
                quit()

            for host in self.config['hosts']:
                port = a.select_port(host)
                auth = a.select_auth_method(host)
                tun = a.establish_tunnel(host, port, auth)
                self.tunnels.append(tun)
                remote = a.establish_remote_session(host, port, auth)
                self.remotes.append(remote)
                if remote.test_conn() is False:
                    self.logger.info("SSH connection failed ... exiting")
                    quit()
                tun_port = random.randint(32768, 61000)
                a.install_lime(host, remote, tun_port)
                a.dump_memory(self.config, host, tun, remote, tun_port)
                a.cleanup_lime(remote)

        except KeyboardInterrupt:
            for tunnel in self.tunnels:
                tunnel.cleanup()
            for remote in self.remotes:
                a.cleanup_lime(remote)
                remote.cleanup()
            sys.exit()

if __name__ == "__main__":
    ms = margaritashotgun()
    ms.run()
