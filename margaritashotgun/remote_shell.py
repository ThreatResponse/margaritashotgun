import paramiko
from paramiko import AuthenticationException, SSHException
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
from socket import error as SocketError
from margaritashotgun.auth import AuthMethods
from margaritashotgun.exceptions import *
import logging

logger = logging.getLogger(__name__)


class Commands(Enum):
    mem_size = "cat /proc/meminfo | grep MemTotal | awk '{ print $2 }'"
    kernel_version = "uname -r"
    lime_pattern = "{0}:{1}"
    lime_check = "netstat -lnt | grep {0}"
    load_lime = 'sudo insmod {0} "path=tcp:{1}" format={2}'
    unload_lime = "sudo pkill insmod; sudo rmmod lime"


class RemoteShell():

    def __init__(self, max_async_threads=2):
        """
        :type args: int
        :param args: maximun number of async command executors
        """

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.executor = ThreadPoolExecutor(max_workers=max_async_threads)
        self.futures = []

    def connect(self, auth, address, port):
        """
        Creates an ssh session to a remote host

        :type auth: :py:class:`margaritashotgun.auth.AuthMethods`
        :param auth: Authentication object
        :type address: str
        :param address: remote server address
        :type port: int
        :param port: remote server port
        """
        self.username = auth.username
        self.address = address
        self.port = port
        try:
            logger.debug(("{0}: paramiko client connecting to "
                          "{0}:{1} with {2}".format(address,
                                                    port,
                                                    auth.method)))
            if auth.method == AuthMethods.key:
                self.connect_with_key(auth.username, auth.key, address, port)
            elif auth.method == AuthMethods.password:
                self.connect_with_password(auth.username, auth.password,
                                           address, port)
            else:
                raise AuthenticationMethodMissingError()
            logger.debug(("{0}: paramiko client connected to "
                          "{0}:{1}".format(address, port)))
        except (AuthenticationException, SSHException, SocketError) as ex:
            raise SSHConnectionError("{0}:{1}".format(address, port), ex)


    def connect_with_password(self, username, password, address, port):
        """
        Create an ssh session to a remote host with a username and password

        :type username: str
        :param username: username used for ssh authentication
        :type password: str
        :param password: password used for ssh authentication
        :type address: str
        :param address: remote server address
        :type port: int
        :param port: remote server port
        """
        self.ssh.connect(username=username,
                         password=password,
                         hostname=address,
                         port=port)

    def connect_with_key(self, username, key, address, port):
        """
        Create an ssh session to a remote host with a username and rsa key

        :type username: str
        :param username: username used for ssh authentication
        :type key: :py:class:`paramiko.key.RSAKey`
        :param key: paramiko rsa key used for ssh authentication
        :type address: str
        :param address: remote server address
        :type port: int
        :param port: remote server port
        """
        self.ssh.connect(hostname=address,
                         port=port,
                         username=username,
                         pkey=key)

    def execute(self, command):
        """
        Executes command on remote hosts

        :type command: str
        :param command: command to be run on remote host
        """
        logger.debug('{0}: executing "{1}"'.format(self.address, command))
        stdin, stdout, stderr = self.ssh.exec_command(command)
        return dict(zip(['stdin', 'stdout', 'stderr'],
                        [stdin, stdout, stderr]))

    def execute_async(self, command, callback=None):
        """
        Executes command on remote hosts without blocking

        :type command: str
        :param command: command to be run on remote host
        :type callback: function
        :param callback: function to call when execution completes
        """
        logger.debug(('{0}: execute async "{1}"'
                      'with callback {2}'.format(self.address, command,
                                                 callback)))
        future = self.executor.submit(self.execute, command)
        if callback is not None:
            future.add_done_callback(callback)
        return future

    def decode(self, stream, encoding='utf-8'):
        """
        Convert paramiko stream into a string

        :type stream:
        :param stream: stream to convert
        :type encoding: str
        :param encoding: stream encoding
        """
        data = stream.read().decode(encoding).strip("\n")
        if data != "":
            logger.debug(('{0}: decoded "{1}" with encoding '
                          '{2}'.format(self.address, data, encoding)))
        return data

    def upload_file(self, local_path, remote_path):
        """
        Upload a file from the local filesystem to the remote host

        :type local_path: str
        :param local_path: path of local file to upload
        :type remote_path: str
        :param remote_path: destination path of upload on remote host
        """
        logger.debug("{0}: uploading {1} to {0}:{2}".format(self.address,
                                                            local_path,
                                                            remote_path))
        try:
            sftp = self.ssh.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
        except SSHException as ex:
            logger.warn(("{0}: LiME module upload failed with exception:"
                         "{1}".format(self.address, ex)))

    def cleanup(self):
        """
        Release resources used during shell execution
        """
        for future in self.futures:
            future.cancel()
        self.executor.shutdown(wait=10)
        self.ssh.close()
