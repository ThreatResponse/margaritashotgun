import errno
import logging
import paramiko
from paramiko import AuthenticationException, SSHException
import select
import socket
import threading
from margaritashotgun.exceptions import *

try:
    import socketserver
except ImportError:
    import SocketServer as socketserver

logger = logging.getLogger(__name__)


class SSHTunnel():

    def __init__(self):
        self.transport = None
        self.forward = None
        self.username = None
        self.address = None
        self.local_port = None
        self.remote_address = None
        self.remote_port = None

    def configure(self, transport, auth, address, port):
        """
        Connect paramiko transport

        :type auth: :py:class`margaritashotgun.auth.AuthMethods`
        :param auth: authentication object
        :type address: str
        :param address: remote server ip or hostname
        :type port: int
        :param port: remote server port
        :type hostkey: :py:class:`paramiko.key.HostKey`
        :param hostkey: remote host ssh server key
        """

        self.transport = transport
        self.username = auth.username
        self.address = address
        self.port = port

    def start(self, local_port, remote_address, remote_port):
        """
        Start ssh tunnel

        type: local_port: int
        param: local_port: local tunnel endpoint ip binding
        type: remote_address: str
        param: remote_address: Remote tunnel endpoing ip binding
        type: remote_port: int
        param: remote_port: Remote tunnel endpoint port binding
        """
        self.local_port = local_port
        self.remote_address = remote_address
        self.remote_port = remote_port

        logger.debug(("Starting ssh tunnel {0}:{1}:{2} for "
                      "{3}@{4}".format(local_port, remote_address, remote_port,
                                       self.username, self.address)))
        self.forward = Forward(local_port,
                               remote_address,
                               remote_port,
                               self.transport)
        self.forward.start()

    def cleanup(self):
        """
        Cleanup resources used during execution
        """
        if self.local_port is not None:
            logger.debug(("Stopping ssh tunnel {0}:{1}:{2} for "
                          "{3}@{4}".format(self.local_port,
                                           self.remote_address,
                                           self.remote_port,
                                           self.username,
                                           self.address)))
            if self.forward is not None:
                self.forward.stop()
                self.forward.join()
            if self.transport is not None:
                self.transport.close()


class Forward(threading.Thread):

    def __init__(self, local_port, remote_address, remote_port, transport):
        """
        type: local_port: int
        param: local_port: local tunnel endpoint ip binding
        type: remote_address: str
        param: remote_address: Remote tunnel endpoing ip binding
        type: remote_port: int
        param: remote_port: Remote tunnel endpoint port binding
        type: transport: :py:class:`paramiko.Transport`
        param: transport: Paramiko ssh transport
        """
        super(Forward, self).__init__()
        self.local_port = local_port
        self.remote_address = remote_address
        self.remote_port = remote_port
        self.transport = transport

    def run(self):
        self.forward_tunnel(self.local_port,
                            self.remote_address,
                            self.remote_port,
                            self.transport)

    def forward_tunnel(self, local_port, remote_address, remote_port, transport):
        class SubHandler (Handler):
            chain_host = remote_address
            chain_port = remote_port
            ssh_transport = transport
            # Increase window size and support compression data stream.
            ssh_transport.use_compression()
            ssh_transport.window_size = 2147483647
            ssh_transport.packetizer.REKEY_PACKETS = pow(2, 40)
            ssh_transport.packetizer.REKEY_BYTES = pow(2, 40)

        self.server = ForwardServer(('', local_port), SubHandler)
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()

class ForwardServer (socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


class Handler (socketserver.BaseRequestHandler):

    def handle(self):
        try:
            channel = self.ssh_transport.open_channel('direct-tcpip',
                                                   (self.chain_host,
                                                    self.chain_port),
                                                   self.request.getpeername())

        except Exception as ex:
            logger.debug(("Incoming request to {0}:{1} failed: "
                          "{2}".format(self.chain_host, self.chain_port, ex)))
            return
        if channel is None:
            logger.debug(("Incoming request to {0}:{1} was "
                          "rejected.".format(self.chain_host, self.chain_port)))
            return

        logger.debug('tunnel open {} -> {} -> {}'.format(
                     self.request.getpeername(),
                     channel.getpeername(),
                     (self.chain_host, self.chain_port)))
        while True:
            try:
                r, w, x = select.select([self.request, channel], [], [])
                if self.request in r:
                    data = self.request.recv(65536)
                    if len(data) == 0:
                        break
                    channel.send(data)
                if channel in r:
                    data = channel.recv(65536)
                    if len(data) == 0:
                        break
                    self.request.send(data)
            except socket.error as ex:
                if ex.errno != errno.ECONNRESET:
                    raise
                else:
                    pass

        try:
            peername = self.request.getpeername()
        except socket.error as ex:
            if ex.errno == errno.ENOTCONN:
                channel.close()
                self.request.close()
                logger.debug('ssh tunnel closed remote end disconnected')
                return
        channel.close()
        self.request.close()
        logger.debug('ssh tunnel closed from {0}'.format(peername))
