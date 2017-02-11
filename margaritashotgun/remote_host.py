import sys
import logging
import logging.handlers
import random
import time
from datetime import datetime
from margaritashotgun.exceptions import *
from margaritashotgun.auth import Auth
from margaritashotgun.remote_shell import RemoteShell, Commands
from margaritashotgun.ssh_tunnel import SSHTunnel
from margaritashotgun.repository import Repository
from margaritashotgun.memory import Memory, OutputDestinations
from margaritashotgun.util import parser

try:
    from logging.handlers import QueueHandler
except ImportError:
    from logutils.queue import QueueHandler


def _init(queue):
    global log_queue
    log_queue = queue

def process(conf):
    """
    """
    jump_host = conf['host']['jump_host']
    remote_addr = conf['host']['addr']
    remote_port = conf['host']['port']
    username = conf['host']['username']
    password = conf['host']['password']
    lime_module = conf['host']['module']
    filename = conf['host']['filename']
    key = conf['host']['key']
    bucket = conf['aws']['bucket']
    progressbar = conf['host']['progressbar']
    tunnel_addr = '127.0.0.1'
    tunnel_port = random.randint(10000, 30000)
    remote_module_path = '/tmp/lime.ko'

    repository_enabled = conf['repository']['enabled']
    repository_url = conf['repository']['url']
    repository_manifest = conf['repository']['manifest']
    repository_gpg_verify = conf['repository']['gpg_verify']

    queue_handler = QueueHandler(log_queue)
    logger = logging.getLogger('margaritashotgun')
    logger.addHandler(queue_handler)

    if bucket is not None:
        dest = OutputDestinations.s3
    else:
        dest = OutputDestinations.local

    if filename is None:
        tm = int(time.time())
        dt = datetime.utcfromtimestamp(tm).isoformat()
        filename = "{0}-{1}-mem.lime".format(remote_addr, dt)

    try:
        host = Host()
        host.connect(username, password, key, remote_addr, remote_port,
                     jump_host)
        host.start_tunnel(tunnel_port, tunnel_addr, tunnel_port)
        if lime_module is None:
            kernel_version = host.kernel_version()
            if repository_enabled:
                repo = Repository(repository_url, repository_gpg_verify)
                repo.init_gpg()
                lime_module = repo.fetch(kernel_version, repository_manifest)
                host.upload_module(lime_module)
            else:
                raise KernelModuleNotProvidedError(kernel_version)
        else:
            host.upload_module(lime_module, remote_module_path)

        host.load_lime(remote_module_path, tunnel_port)
        lime_loaded = host.wait_for_lime(tunnel_port)

        if lime_loaded:
            result = host.capture_memory(dest, filename, bucket, progressbar)
        else:
            logger.debug("lime failed to load on {0}".format(remote_addr))
            result = False

        logger.removeHandler(queue_handler)
        queue_handler.close()
        host.cleanup()

        return (remote_addr, result)
    except SSHConnectionError as ex:
        logger.error(ex)
        logger.removeHandler(queue_handler)
        queue_handler.close()
        return (remote_addr, False)
    except KeyboardInterrupt as ex:
        logger.removeHandler(queue_handler)
        queue_handler.close()
        host.cleanup()
        return (remote_addr, False)
    except (SSHCommandError, Exception) as ex:
        logger.error(ex)
        logger.removeHandler(queue_handler)
        queue_handler.close()
        host.cleanup()
        return (remote_addr, False)

class Host():

    def __init__(self):
        """
        """
        self.memory = None
        self.tunnel = None
        self.shell = None
        self.remote_addr = None
        self.remote_port = None
        self.tunnel_addr = "127.0.0.1"
        self.tunnel_port = None
        self.shell = RemoteShell()
        self.commands = Commands
        self.tunnel = SSHTunnel()
        self.net_parser = parser.ProcNetTcpParser()

    def connect(self, username, password, key, address, port, jump_host):
        """
        Connect ssh tunnel and shell executor to remote host

        :type username: str
        :param username: username for authentication
        :type password: str
        :param password: password for authentication, may be used to unlock rsa key
        :type key: str
        :param key: path to rsa key for authentication
        :type address: str
        :param address: address for remote host
        :type port: int
        :param port: ssh port for remote host
        """
        if port is None:
            self.remote_port = 22
        else:
            self.remote_port = int(port)

        auth = Auth(username=username, password=password, key=key)
        if jump_host is not None:
            jump_auth = Auth(username=jump_host['username'],
                             password=jump_host['password'],
                             key=jump_host['key'])
            if jump_host['port'] is None:
                jump_host['port'] = 22
        else:
            jump_auth = None
        self.shell.connect(auth, address, self.remote_port, jump_host, jump_auth)
        transport = self.shell.transport()
        self.tunnel.configure(transport, auth, address, self.remote_port)
        self.remote_addr = address

    def start_tunnel(self, local_port, remote_address, remote_port):
        """
        Start ssh forward tunnel

        :type local_port: int
        :param local_port: local port binding for ssh tunnel
        :type remote_address: str
        :param remote_address: remote tunnel endpoint bind address
        :type remote_port: int
        :param remote_port: remote tunnel endpoint bind port
        """
        self.tunnel.start(local_port, remote_address, remote_port)
        self.tunnel_port = local_port

    def mem_size(self):
        """
        Returns the memory size in bytes of the remote host
        """
        result = self.shell.execute(self.commands.mem_size.value)
        stdout = self.shell.decode(result['stdout'])
        stderr = self.shell.decode(result['stderr'])
        return int(stdout)

    def kernel_version(self):
        """
        Returns the kernel kernel version of the remote host
        """
        result = self.shell.execute(self.commands.kernel_version.value)
        stdout = self.shell.decode(result['stdout'])
        stderr = self.shell.decode(result['stderr'])
        return stdout

    def wait_for_lime(self, listen_port, listen_address="0.0.0.0",
                      max_tries=20, wait=1):
        """
        Wait for lime to load unless max_retries is exceeded

        :type listen_port: int
        :param listen_port: port LiME is listening for connections on
        :type listen_address: str
        :param listen_address: address LiME is listening for connections on
        :type max_tries: int
        :param max_tries: maximum number of checks that LiME has loaded
        :type wait: int
        :param wait: time to wait between checks
        """
        tries = 0
        pattern = self.commands.lime_pattern.value.format(listen_address,
                                                          listen_port)
        lime_loaded = False
        while tries < max_tries and lime_loaded is False:
            lime_loaded = self.check_for_lime(pattern)
            tries = tries + 1
            time.sleep(wait)
        return lime_loaded

    def check_for_lime(self, pattern):
        """
        Check to see if LiME has loaded on the remote system

        :type pattern: str
        :param pattern: pattern to check output against
        :type listen_port: int
        :param listen_port: port LiME is listening for connections on
        """
        check = self.commands.lime_check.value
        lime_loaded = False
        result = self.shell.execute(check)
        stdout = self.shell.decode(result['stdout'])
        connections = self.net_parser.parse(stdout)

        for conn in connections:
            local_addr, remote_addr = conn
            if local_addr == pattern:
                lime_loaded = True
                break

        return lime_loaded

    def upload_module(self, local_path=None, remote_path="/tmp/lime.ko"):
        """
        Upload LiME kernel module to remote host

        :type local_path: str
        :param local_path: local path to lime kernel module
        :type remote_path: str
        :param remote_path: remote path to upload lime kernel module
        """
        if local_path is None:
            raise FileNotFoundFoundError(local_path)
        self.shell.upload_file(local_path, remote_path)

    def load_lime(self, remote_path, listen_port, dump_format='lime'):
        """
        Load LiME kernel module from remote filesystem

        :type remote_path: str
        :param remote_path: path to LiME kernel module on remote host
        :type listen_port: int
        :param listen_port: port LiME uses to listen to remote connections
        :type dump_format: str
        :param dump_format: LiME memory dump file format
        """
        load_command = self.commands.load_lime.value.format(remote_path,
                                                            listen_port,
                                                            dump_format)
        self.shell.execute_async(load_command)

    def unload_lime(self):
        """
        Remove LiME kernel module from remote host
        """
        self.shell.execute(self.commands.unload_lime.value)

    def capture_memory(self, destination, filename, bucket, progressbar):
        """
        """
        mem_size = self.mem_size()
        mem = Memory(self.remote_addr, mem_size, progressbar=progressbar)
        mem.capture(self.tunnel_addr, self.tunnel_port, destination=destination,
                    filename=filename, bucket=bucket)

    # TODO: move this to RemoteShell?
    # TODO: eventually hook this in to our logger
    # TODO: doc string
    def log_async_result(self, future):
        """
        """
        result = future.result()
        stdout = self.shell.decode(result['stdout'])
        stderr = self.shell.decode(result['stderr'])
        print(stdout)
        print(stderr)

    def cleanup(self):
        """
        Release resources used by supporting classes
        """
        try:
            self.unload_lime()
        except AttributeError as ex:
            pass
        self.tunnel.cleanup()
        self.shell.cleanup()
