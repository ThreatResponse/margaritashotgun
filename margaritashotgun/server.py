#!/usr/bin/env python

import paramiko
import threading
import time

class server():
    def __init__(self, server, port, username, verbose=False):
        self.ssh      = paramiko.SSHClient()
        self.server   = server
        self.port     = port
        self.username = username
        self.threads  = []
        self.verbose  = False
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect_with_password(self, password):
        self.ssh.connect(hostname = self.server,
                         port     = self.port,
                         username = self.username,
                         password = password)

    def connect_with_keyfile(self, private_key_path):
        key = paramiko.RSAKey.from_private_key_file(private_key_path)
        self.ssh.connect(hostname = self.server,
                         port     = self.port,
                         username = self.username,
                         pkey     = key)

    def connect_with_encrypted_keyfile(self, private_key_path, password):
        key = paramiko.RSAKey.from_private_key_file(private_key_path, password=password)
        self.ssh.connect(hostname = self.server,
                         port     = self.port,
                         username = self.username,
                         pkey     = key)

    def test_conn(self):
        try:
            stdin, stdout, stderr = self.ssh.exec_command('ls -a')
            #for line in stdout:
            #    print(line.strip('\n'))
            if stdin != None:
                connection_status = True
            else:
                connection_status = False
        #TODO: (joel) use specific exceptions
        except Exception as e:
            connection_status = False
        return connection_status

    def get_mem_size(self):
        stdin, stdout, stderr = self.ssh.exec_command("cat /proc/meminfo | grep MemTotal | awk '{ print $2 }'")
        for line in stdout:
            memsize = int(line.strip('\n'))
        return memsize*1024 #convert from Kb to bytes

    def wait_for_lime(self, port=4000):
        tries = 0
        lime_listener = "0.0.0.0:{}".format(port)
        command = "netstat -lnt | grep {}".format(port)
        lime_loaded = False
        while tries < 60 and lime_loaded == False:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            output = stdout.read().decode('utf-8').strip("\n")
            if lime_listener in output:
                lime_loaded = True
            tries = tries + 1
            time.sleep(1)
        return lime_loaded


    def upload_file(self, local_path, remote_path):
        sftp = self.ssh.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()

    def execute(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        if self.verbose:
            for line in stdout:
                print(line.strip('\n'))

    def execute_async(self, command):
        worker = async_worker(command, self.ssh)
        self.threads.append(worker)
        #worker.daemon=True
        worker.start()

    def cleanup(self):
        self.ssh.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.ssh.close()

class async_worker(threading.Thread):

    def __init__(self, command, ssh):
        super(async_worker, self).__init__()
        self.command = command
        self.ssh     = ssh

    def run(self):
        stdin, stdout, stderr = self.ssh.exec_command(self.command, timeout=60)

