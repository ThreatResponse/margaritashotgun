#!/usr/bin/env python

from multiprocessing import Pool
import logging
import random
from . import cli
from . import api


def multi_run(config):
    logger = logging.getLogger(config['logger'])
    c = cli.cli(logger)
    a = api.api(logger)
    remotes = []
    tunnels = []
    try:
        if a.invalid_config(config):
            logger.info("config_verify_fail exiting")
            return False

        host = config['host']
        port = a.select_port(host)
        auth = a.select_auth_method(host)
        tun = a.establish_tunnel(host, port, auth)
        tunnels.append(tun)
        remote = a.establish_remote_session(host, port, auth)
        remotes.append(remote)
        if remote.test_conn() is False:
            logger.info("SSH connection failed ... exiting")
            return False
        tun_port = random.randint(32768, 61000)
        a.install_lime(host, remote, tun_port)
        draw_pbar = config['pbar']
        a.dump_memory(config, host, tun, remote, tun_port, draw_pbar)
        a.cleanup_lime(remote)
        return True

    except KeyboardInterrupt:
        for tunnel in tunnels:
            tunnel.cleanup()
        for remote in remotes:
            a.cleanup_lime(remote)
            remote.cleanup()
            sys.exit()


class master():

    def __init__(self, logger, hosts, workers):
        self.logger = logger
        self.hosts = hosts
        self.workers = workers

    def start_workers(self):
        pool = Pool(self.workers)
        results = pool.map(multi_run, self.hosts)
        pool.close()
        pool.join()
        total = len(results)
        success = 0
        for result in results:
            if result:
                success = success + 1
        self.logger.info("{}/{} successful memory dumps".format(success,
                                                                total))
