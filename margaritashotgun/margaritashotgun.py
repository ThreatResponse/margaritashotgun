#!/usr/bin/env python

import random
from cli import cli
from api import api

class margaritashotgun():

    def run(self):
        c = cli()
        a = api()
        self.config = c.parse_args()
        # check config is valid
        if a.invalid_config(self.config):
            print("config_verify_fail exiting")
            quit()

        for host in self.config['hosts']:
            port   = a.select_port(host)
            auth   = a.select_auth_method(host)
            tun    = a.establish_tunnel(host, port, auth)
            remote = a.establish_remote_session(host, port, auth)
            if remote.test_conn() == False:
                print("SSH connection failed ... exiting")
                quit()
            tun_port = random.randint(32768, 61000)
            print(tun_port)
            a.install_lime(host, remote, tun_port)
            a.dump_memory(self.config, host, tun, remote, tun_port)

if __name__=="__main__":
    ms = margaritashotgun()
    ms.run()

