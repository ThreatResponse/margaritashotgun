#!/usr/bin/env python

import multiprocessing
from multiprocessing import Pool
import logging
import random
from . import cli
from . import api
from . import multilogger


def multi_run(config):
    log_dir = config['logging']['dir']
    log_prefix = config['logging']['prefix']
    if log_dir[-1:] != '/' and log_dir != '':
        log_dir = log_dir + "/"

    if log_prefix[-1:] != '-' and log_prefix != '':
        log_prefix = log_prefix + "-"

    logfile = "{}{}{}-memcapture-json.log".format(log_dir, log_prefix,
                                       config['host']['addr'])
    desc = "{} action".format(config['logging']['logger'])
    logger = multilogger.multilogger(config['logging']['logger'], logfile,
                                     desc=desc)

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
        cpu_count = multiprocessing.cpu_count()
        if workers == 'auto':
            workers = cpu_count
        if workers > len(self.hosts):
            self.workers = len(self.hosts)
        else:
            self.workers = int(workers)

        if self.workers > 1:
            draw_pbar = False
        else:
            draw_pbar = True

        for host in self.hosts:
            host['pbar'] = draw_pbar

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
