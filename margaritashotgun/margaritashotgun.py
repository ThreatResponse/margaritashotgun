#!/usr/bin/env python

class margaritashotgun():

    def run(self):
        c = cli()
        c.run()


if __name__=="__main__":
    ms = margaritashotgun()
    ms.run()

#!/usr/bin/env python
#import os
#import argparse
#from server import server
#from tunnel import tunnel
#import yaml
#from memory import memory
#
#class cli():
#
#    def __init__(self):
#        self.config = self.parse_args()
#
#    def module_missing(self, module_name):
#        try:
#            __import__(module_name)
#        except ImportError as e:
#            return True
#        else:
#            return False
#
#    def parse_args(self):
#        parser = argparse.ArgumentParser(description='TODO description')
#        parser.add_argument('-s', '--server', help='hostname or ip of target server')#,
#        parser.add_argument('-P', '--port', help='ssh port on remote server')#,
#        parser.add_argument('-u', '--username', help='username for ssh connection')#,
#        parser.add_argument('-p', '--password', help='password user, or for encrypted keyfile when used with -k argument')
#        parser.add_argument('-k', '--keyfile', help='path to rsa key for ssh connection')
#        parser.add_argument('-m', '--module', help='path to kernel lime kernel module')#,
#        parser.add_argument('-c', '--config', help='path to config.yml')
#
#        arguments = parser.parse_args()
#
#        if arguments.keyfile:
#            if self.verify_file_path(arguments.keyfile) is False:
#                print("Invalid private key path: {0}".format(arguments.keyfile))
#                quit()
#
#        if arguments.module:
#            if self.verify_file_path(arguments.module) is False:
#                print("Invalid kernel module path: {0}".format(arguments.module))
#                quit()
#
#        if arguments.config is None:
#            #TODO: (joel) check default location for creds
#            #TODO  (joel) specify bucket + creds file + cred pair with flags
#            config = { 'aws':
#                       { 'bucket':     None,
#                         'key':        None,
#                         'secret':     None},
#                       'hosts':
#                       [ { 'addr':     arguments.server,
#                           'port':     arguments.port,
#                           'username': arguments.username,
#                           'password': arguments.password,
#                           'keyfile':  arguments.keyfile,
#                           'module':   arguments.module } ] }
#        else:
#            try:
#                with open(arguments.config, 'r') as stream:
#                    try:
#                        config = yaml.load(stream)
#                    except yaml.YAMLError as ex:
#                        print('Invalid config format: {0}'.format(ex))
#                        quit()
#            except IOError as ex:
#                print('Invalid config path: {0}'.format(arguments.config_file))
#                quit()
#
#        return config
#
#    def verify_file_path(self, path):
#        if os.path.exists(path):
#            return True
#        else:
#            return False
#
#    def run(self):
#        for host in self.config['hosts']:
#            if host['port']:
#                port = int(host['port'])
#            else:
#                port = 22
#            ssh_tunnel = tunnel(host['addr'], port, host['username'])
#            remote = server(host['addr'], port, host['username'])
#            if 'keyfile' in host and 'password' in host:
#
#                ssh_tunnel.connect_with_encrypted_keyfile(host['keyfile'],
#                                                          host['password'])
#                remote.connect_with_encrypted_keyfile(host['keyfile'],
#                                                      host['password'])
#            elif 'keyfile' in host:
#                ssh_tunnel.connect_with_keyfile(host['keyfile'])
#                remote.connect_with_keyfile(host['keyfile'])
#            elif 'password' in host:
#                ssh_tunnel.connect_with_password(host['password'])
#                remote.connect_with_password(host['password'])
#            else:
#                print("no authentication method specified")
#                quit()
#            status_ok = remote.test_conn()
#            if status_ok == False:
#                print("SSH connection failed ... exiting")
#                quit()
#            memsize = remote.get_mem_size()
#            remote.upload_file(host['module'], 'lime.ko')
#            remote.execute_async('sudo insmod ./lime.ko "path=tcp:4000 format=lime"')
#            ssh_tunnel.start(4000, '127.0.0.1', 4000)
#            lime_loaded = remote.wait_for_lime()
#            if lime_loaded:
#                mem = memory('127.0.0.1', 4000, memsize)
#                # unpack config items
#                try:
#                    bucket = self.config['aws']['bucket']
#                    key    = self.config['aws']['key']
#                    secret = self.config['aws']['secret']
#                except KeyError as e:
#                    bucket = None
#                    key    = None
#                    secret = None
#                    #print(e)
#
#                filename='{}-mem.lime'.format(host['addr'])
#
#                if bucket != None and key != None and secret != None:
#                    print('{} dumping memory to s3://{}/{}'.format(host['addr'],
#                                                                   bucket,
#                                                                   filename))
#                    mem.to_s3(key_id=key,
#                                  secret_key=secret,
#                                  bucket=bucket,
#                                  filename=filename)
#                else:
#                    print('{} dumping memory to {}'.format(host['addr'],
#                                                           filename))
#                    mem.to_file(filename)
#            else:
#                print("Lime failed to load ... exiting")
#            remote.execute('sudo rmmod lime.ko')
#            ssh_tunnel.stop()
#
#if __name__=='__main__':
#    c = cli()
#    c.run()
