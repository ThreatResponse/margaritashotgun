import sys
import logging
import logging.handlers
import random
import time
from margaritashotgun.exceptions import *
from margaritashotgun.auth import Auth
from margaritashotgun.remote_shell import RemoteShell, Commands
from margaritashotgun.ssh_tunnel import SSHTunnel
from margaritashotgun.repository import Repository
from margaritashotgun.memory import Memory, OutputDestinations

try:
    from logging.handlers import QueueHandler
except ImportError:
    from logutils.queue import QueueHandler

# TODO: add config item to resolve modules automatically
# TODO: add config item repository url (only suports s3 bucket for now

def _init(queue):
    global log_queue
    log_queue = queue

def process(conf):
    """
    """

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

    queue_handler = QueueHandler(log_queue)
    logger = logging.getLogger('margaritashotgun')
    logger.addHandler(queue_handler)

    if bucket is not None:
        dest = OutputDestinations.s3
    else:
        dest = OutputDestinations.local

    if filename is None:
        filename = "{0}-mem.lime".format(remote_addr)

    try:
        host = Host()
        host.connect(username, password, key, remote_addr, remote_port)
        host.start_tunnel(tunnel_port, tunnel_addr, tunnel_port)
        if lime_module is None:
            kernel_version = host.kernel_version()
            if repository_enabled:
                repo = Repository(repository_url)
                match = repo.search_modules(kernel_version)
                if match is not None:
                    lime_module = repo.fetch_module(match)
                    host.upload_module(lime_module)
                else:
                    raise KernelModuleNotFoundError(kernel_version, repo.url)
            else:
                # TODO: prompt user to search repository when running interactively
                raise KernelModuleNotProvidedError(kernel_version)
        else:
            host.upload_module(lime_module, remote_module_path)

        host.load_lime(remote_module_path, tunnel_port)
        lime_loaded = host.wait_for_lime(tunnel_port)

        if lime_loaded:
            result = host.capture_memory(dest, filename, bucket, progressbar)
        else:
            result = False

        logger.removeHandler(queue_handler)
        queue_handler.close()
        host.cleanup()

        return (remote_addr, result)
    except KeyboardInterrupt:
        logger.removeHandler(queue_handler)
        queue_handler.close()
        host.cleanup()
        return (remote_addr, False)
    except Exception as ex:
        logger.removeHandler(queue_handler)
        queue_handler.close()
        host.cleanup()
        logger.critical(ex)
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

    def connect(self, username, password, key, address, port):
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
            self.remote_port = port
        auth = Auth(username=username, password=password, key=key)
        self.tunnel.connect(auth, address, self.remote_port)
        self.shell.connect(auth, address, self.remote_port)
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
            lime_loaded = self.check_for_lime(pattern, listen_port)
            tries = tries + 1
            time.sleep(wait)
        return lime_loaded

    def check_for_lime(self, pattern, listen_port):
        """
        Check to see if LiME has loaded on the remote system

        :type pattern: str
        :param pattern: pattern to check output against
        :type listen_port: int
        :param listen_port: port LiME is listening for connections on
        """
        check = self.commands.lime_check.value.format(listen_port)
        result = self.shell.execute(check)
        stdout = self.shell.decode(result['stdout'])
        stderr = self.shell.decode(result['stderr'])
        if pattern in stdout:
            return True
        else:
            return False

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
