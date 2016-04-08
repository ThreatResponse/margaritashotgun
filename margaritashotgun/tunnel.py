#!/usr/bin/env python

import paramiko
import socket
import select
import sys
import threading

try:
    import socketserver
except ImportError:
    import SocketServer as socketserver

class tunnel():

    def __init__(self, ssh_host, ssh_port, username, verbose=False):
        self.transport = paramiko.Transport((ssh_host, ssh_port))
        self.username  = username
        self.verbose   = verbose

    def connect_with_password(self,password):
        self.transport.connect(hostkey  = None,
                               username = self.username,
                               password = password)

    def connect_with_keyfile(self, private_key_path):
        key = paramiko.RSAKey.from_private_key_file(private_key_path)
        self.transport.connect(hostkey  = None,
                               username = self.username,
                               pkey     = key)

    def connect_with_encrypted_keyfile(self, private_key_path, password):
        key = paramiko.RSAKey.from_private_key_file(private_key_path, password=password)
        self.transport.connect(hostkey  = None,
                               username = self.username,
                               pkey     = key)

    def start(self, local_port, remote_host, remote_port):
        self.thread = forward(local_port,
                              remote_host,
                              remote_port,
                              self.transport,
                              self.verbose)
        self.thread.start()

    def stop(self):
        self.thread.stop()
        self.thread.join()

class ForwardServer (socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True

class Handler (socketserver.BaseRequestHandler):

    def handle(self):
        try:
            chan = self.ssh_transport.open_channel('direct-tcpip',
                                                   (self.chain_host, self.chain_port),
                                                   self.request.getpeername())
        except Exception as e:
            self.log('Incoming request to %s:%d failed: %s' % (self.chain_host,
                                                              self.chain_port,
                                                              repr(e)))
            return
        if chan is None:
            self.log('Incoming request to %s:%d was rejected by the SSH server.' %
                    (self.chain_host, self.chain_port))
            return

        self.log('Connected!  Tunnel open %r -> %r -> %r' % (self.request.getpeername(),
                                                            chan.getpeername(), (self.chain_host, self.chain_port)))
        while True:
            r, w, x = select.select([self.request, chan], [], [])
            if self.request in r:
                data = self.request.recv(1024)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break
                self.request.send(data)

        peername = self.request.getpeername()
        chan.close()
        self.request.close()
        self.log('Tunnel closed from %r' % (peername,))

    def log(self, string):
        if self.verbose:
            print(string)

class forward(threading.Thread):

    def __init__(self, local_port, remote_host, remote_port, transport, verbose=False):
        super(forward, self).__init__()
        self.local_port  = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.transport   = transport
        self.verbose     = verbose


    def run(self):
        self.forward_tunnel(self.local_port,
                            self.remote_host,
                            self.remote_port,
                            self.transport)

    def forward_tunnel(self, local_port, remote_host, remote_port, transport):
        class SubHandler (Handler):
            chain_host    = remote_host
            chain_port    = remote_port
            ssh_transport = transport
            verbose       = self.verbose
        self.server = ForwardServer(('', local_port), SubHandler)
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()

