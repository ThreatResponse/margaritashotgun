#!/usr/bin/env python

from server import server
from tunnel import tunnel
from memory import memory

class api():

    #def __init__(config):
    #    self.config = config

    def test(self):
        print("test")

    # return false if config is valid
    def invalid_config(self, config):
        #print("todo config verify")
        return False

    def port_specified(self, host):
        #return true if a port is specified in the config
        return True

    def select_auth_method(self, host):
        if 'keyfile' in host and 'password' in host:
            auth = 'encrypted_key_file'
        elif 'keyfile' in host:
            auth = 'key_file'
        elif 'password' in host:
            auth = 'password'
        else:
            #TODO(joel): raise exception
            print('no auth method specified')
            quit()
        return auth

    def select_port(self, host):
        if self.port_specified(host):
            port = int(host['port'])
        else:
            port = 22
        return port

    def establish_tunnel(self, host, port, auth):
        tun = tunnel(host['addr'], port, host['username'])
        if auth == 'encrypted_key_file':
            tun.connect_with_encrypted_keyfile(host['keyfile'],
                                               host['password'])
        elif auth == 'key_file':
            tun.connect_with_keyfile(host['keyfile'])
        elif auth == 'password':
            tun.connect_with_password(host['password'])
        else:
            #TODO(joel): raise exception
            print('no auth method specified')
            quit()
        return tun

    def establish_remote_session(self, host, port, auth):
        rem = server(host['addr'], port, host['username'])
        if auth == 'encrypted_key_file':
            rem.connect_with_encrypted_keyfile(host['keyfile'],
                                                  host['password'])
        elif auth == 'key_file':
            rem.connect_with_keyfile(host['keyfile'])
        elif auth == 'password':
            rem.connect_with_password(host['password'])
        else:
            #TODO(joel): raise exception
            print('no auth method specified')
            quit()
        return rem

    def install_lime(self, host, remote, tun_port):
        remote.upload_file(host['module'], 'lime.ko')
        command = 'sudo insmod ./lime.ko "path=tcp:{} format=lime"'.format(tun_port)
        remote.execute_async(command)

    def dump_memory(self, config, host, tunnel, remote, tun_port):
        tunnel.start(tun_port, '127.0.0.1', tun_port)
        lime_loaded = remote.wait_for_lime(port=tun_port)
        memsize = remote.get_mem_size()

        if lime_loaded:
            mem = memory('127.0.0.1', tun_port, memsize)
            try:
                bucket = config['aws']['bucket']
                key    = config['aws']['key']
                secret = config['aws']['secret']
            except KeyError as e:
                bucket = None
                key    = None
                secret = None
                #print(e)

            filename='{}-mem.lime'.format(host['addr'])

            if bucket != None and key != None and secret != None:
                print('{} dumping memory to s3://{}/{}'.format(host['addr'],
                                                               bucket,
                                                               filename))
                mem.to_s3(key_id=key,
                          secret_key=secret,
                          bucket=bucket,
                          filename=filename)
            else:
                print('{} dumping memory to {}'.format(host['addr'],
                                                       filename))
                mem.to_file(filename)
        else:
            print("Lime failed to load ... exiting")
        remote.execute('sudo rmmod lime.ko')
        tunnel.stop()

if __name__=="__main__":
    api = api()
    api.test()

