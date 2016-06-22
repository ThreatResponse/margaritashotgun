from enum import Enum
#import threading
import paramiko
from paramiko import AuthenticationException, SSHException
from socket import error as SocketError
from margaritashotgun.exceptions import AuthenticationMethodMissingError
from margaritashotgun.exceptions import SSHConnectionError
from margaritashotgun.auth import AuthMethods

# TODO: remove unused imports
#import datetime
#import time
#import requests
#import xmltodict


class Commands(Enum):
    mem_size = "cat /proc/meminfo | grep MemTotal | awk '{ print $2 }'"
    kernel_version = "uname -r"
    lime_pattern = "{0}:{1}"
    lime_check = "netstat -lnt | grep {0}"

class RemoteShell():
    """
    """

    def __init__(self):
        """
        """
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.s3_prefix = "https://s3.amazonaws.com"
        #self.logger = logger

    def connect(self, auth, address, port=22):
        """
        """
        try:
            if auth.method == AuthMethods.key:
                self.connect_with_key(auth.username, auth.key)
            if auth.method == AuthMethods.password:
                self.connect_with_password(auth.username, auth.password)
            else:
                raise AuthenticationMethodMissingError()
        except (AuthenticationException, SSHException, SocketError) as ex:
            raise SSHConnectionError("{}:{}".format(address, port), ex)


        port = opts['port']
        username = opts['username']
        password = opts['password']
        print("todo")


    def connect_with_password(self, username, password, address, port):
        """
        """
        self.ssh.connect(username=username,
                         password=password,
                         hostname=address,
                         port=port)

    def connect_with_key(self, private_key_path):
        """
        """
        key = paramiko.RSAKey.from_private_key_file(private_key_path)
        self.ssh.connect(hostname=self.address,
                         port=self.port,
                         username=self.username,
                         pkey=key)

    def execute(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        return dict(zip(['stdin', 'stdout', 'stderr'],
                        [stdin, stdout, stderr]))

    # TODO: upload file method
    def upload_file(self, local_path, remote_path):
        try:
            sftp = self.ssh.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
        # TODO: handle specific exceptions
        except Exception as ex:
            print(ex)

    def __del__(self):
        self.ssh.close()


#    def execute_async(self, command):
#        worker = async_worker(command, self.ssh)
#        worker.start()

#    def cleanup(self):
#        self.ssh.close()

#    def __exit__(self, exc_type, exc_value, traceback):
#        self.ssh.close()


#class async_worker(threading.Thread):
#
#    def __init__(self, command, ssh):
#        super(async_worker, self).__init__()
#        self.command = command
#        self.ssh = ssh
#
#    def run(self):
#        stdin, stdout, stderr = self.ssh.exec_command(self.command, timeout=60)
