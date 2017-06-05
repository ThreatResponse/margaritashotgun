import paramiko
from paramiko import AuthenticationException, SSHException, ChannelException
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
    lime_check = "cat /proc/net/tcp"
    load_lime = 'sudo insmod {0} "path=tcp:{1}" format={2}'
    unload_lime = "sudo pkill insmod; sudo rmmod lime"


class RemoteShell():

    def __init__(self, max_async_threads=2):
        """
        :type args: int
        :param args: maximun number of async command executors
        """

        self.jump_host_ssh = None
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.executor = ThreadPoolExecutor(max_workers=max_async_threads)
        self.futures = []

    def connect(self, auth, address, port, jump_host, jump_auth):
        """
        Creates an ssh session to a remote host

        :type auth: :py:class:`margaritashotgun.auth.AuthMethods`
        :param auth: Authentication object
        :type address: str
        :param address: remote server address
        :type port: int
        :param port: remote server port
        """

        try:
            self.target_address = address
            sock = None
            if jump_host is not None:
                self.jump_host_ssh = paramiko.SSHClient()
                self.jump_host_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.connect_with_auth(self.jump_host_ssh, jump_auth,
                                       jump_host['addr'], jump_host['port'], sock)
                transport = self.jump_host_ssh.get_transport()
                dest_addr = (address, port)
                jump_addr = (jump_host['addr'], jump_host['port'])
                channel = transport.open_channel('direct-tcpip', dest_addr,
                                                 jump_addr)
                self.connect_with_auth(self.ssh, auth, address, port, channel)
            else:
                self.connect_with_auth(self.ssh, auth, address, port, sock)
        except (AuthenticationException, SSHException,
                ChannelException, SocketError) as ex:
            raise SSHConnectionError("{0}:{1}".format(address, port), ex)

    def connect_with_auth(self, ssh, auth, address, port, sock):
        """
        """
        logger.debug(("{0}: paramiko client connecting to "
                      "{0}:{1} with {2}".format(address,
                                                port,
                                                auth.method)))
        if auth.method == AuthMethods.key:
            self.connect_with_key(ssh, auth.username, auth.key, address,
                                  port, sock)
        elif auth.method == AuthMethods.password:
            self.connect_with_password(ssh, auth.username, auth.password,
                                       address, port, sock)
        else:
            raise AuthenticationMethodMissingError()
        logger.debug(("{0}: paramiko client connected to "
                      "{0}:{1}".format(address, port)))

    def connect_with_password(self, ssh, username, password, address, port, sock,
                              timeout=20):
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
        ssh.connect(username=username,
                    password=password,
                    hostname=address,
                    port=port,
                    sock=sock,
                    timeout=timeout)

    def connect_with_key(self, ssh, username, key, address, port, sock,
                         timeout=20):
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
        ssh.connect(hostname=address,
                    port=port,
                    username=username,
                    pkey=key,
                    sock=sock,
                    timeout=timeout)

    def transport(self):
        transport = self.ssh.get_transport()
        transport.use_compression(True)
        transport.window_size = 2147483647
        transport.packetizer.REKEY_BYTES = pow(2, 40)
        transport.packetizer.REKEY_PACKETS = pow(2, 40)
        return self.ssh.get_transport()

    def execute(self, command):
        """
        Executes command on remote hosts

        :type command: str
        :param command: command to be run on remote host
        """
        try:
            if self.ssh.get_transport() is not None:
                logger.debug('{0}: executing "{1}"'.format(self.target_address,
                                                           command))
                stdin, stdout, stderr = self.ssh.exec_command(command)
                return dict(zip(['stdin', 'stdout', 'stderr'],
                                [stdin, stdout, stderr]))
            else:
                raise SSHConnectionError(self.target_address,
                                         "ssh transport is closed")
        except (AuthenticationException, SSHException,
                ChannelException, SocketError) as ex:
            logger.critical(("{0} execution failed on {1} with exception:"
                             "{2}".format(command, self.target_address,
                                               ex)))
            raise SSHCommandError(self.target_address, command, ex)

    def execute_async(self, command, callback=None):
        """
        Executes command on remote hosts without blocking

        :type command: str
        :param command: command to be run on remote host
        :type callback: function
        :param callback: function to call when execution completes
        """
        try:
            logger.debug(('{0}: execute async "{1}"'
                          'with callback {2}'.format(self.target_address,
                                                     command,
                                                     callback)))
            future = self.executor.submit(self.execute, command)
            if callback is not None:
                future.add_done_callback(callback)
            return future
        except (AuthenticationException, SSHException,
                ChannelException, SocketError) as ex:
            logger.critical(("{0} execution failed on {1} with exception:"
                             "{2}".format(command, self.target_address,
                                               ex)))
            raise SSHCommandError(self.target_address, command, ex)

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
                          '{2}'.format(self.target_address, data, encoding)))
        return data

    def upload_file(self, local_path, remote_path):
        """
        Upload a file from the local filesystem to the remote host

        :type local_path: str
        :param local_path: path of local file to upload
        :type remote_path: str
        :param remote_path: destination path of upload on remote host
        """
        logger.debug("{0}: uploading {1} to {0}:{2}".format(self.target_address,
                                                            local_path,
                                                            remote_path))
        try:
            sftp = paramiko.SFTPClient.from_transport(self.transport())
            sftp.put(local_path, remote_path)
            sftp.close()
        except SSHException as ex:
            logger.warn(("{0}: LiME module upload failed with exception:"
                         "{1}".format(self.target_address, ex)))

    def cleanup(self):
        """
        Release resources used during shell execution
        """
        for future in self.futures:
            future.cancel()
        self.executor.shutdown(wait=10)
        if self.ssh.get_transport() != None:
            self.ssh.close()
