#!/usr/bin/env python

from progressbar import ProgressBar, Percentage, Bar, ETA, FileTransferSpeed
import errno
import select
import socket
import s3fs


class memory():

    def __init__(self, tunnel_host, tunnel_port, remote_host, memsize,
                 logger, draw_pbar, recv_size=1048576, sock_timeout=2):
        self.tunnel_host = tunnel_host
        self.tunnel_port = tunnel_port
        self.remote_host = remote_host
        self.recv_size = recv_size
        self.memsize = memsize
        self.draw_pbar = draw_pbar
        padding = memsize * 0.03
        self.update_threshold = 1024 * 1024 * 10
        self.maxsize = memsize + padding
        self.transfered = 0
        self.widgets = ['{} '.format(remote_host), Percentage(), ' ', Bar(),
                        ' ', ETA(), ' ', FileTransferSpeed()]
        self.sock_timeout = sock_timeout
        self.logger = logger
        self.progress = 0

    def update_progress_bar(self, complete=False):
        if self.draw_pbar:
            try:
                self.pbar.update(self.transfered)
            except Exception as e:
                self.logger.info("{}-{}: {} exceeds memsize {}".format(
                                 self.remote_host,
                                 e,
                                 self.transfered,
                                 self.maxsize))
            if complete:
                self.pbar.update(self.maxsize)
                self.pbar.finish()
        else:
            percent = int(100 * float(self.transfered) / float(self.maxsize))
            # printe a message at 10%, 20%, etc...
            if percent % 10 == 0:
                if self.progress != percent:
                    self.logger.info("{}: capture {}% complete".format(
                                     self.remote_host, percent))
                    self.progress = percent

    def to_file(self, filename):
        if self.draw_pbar:
            self.pbar = ProgressBar(widgets=self.widgets,
                                    maxval=self.maxsize).start()
            self.pbar.start()
            pbar_update = True

        with open(filename, 'wb') as self.outfile:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.tunnel_host, self.tunnel_port))
            self.sock.settimeout(self.sock_timeout)
            bytes_since_update = 0
            while True:
                try:
                    data = self.sock.recv(self.recv_size)
                    data_length = len(data)
                    if not data:
                        break
                    self.outfile.write(data)
                    self.transfered = self.transfered + data_length
                    bytes_since_update = bytes_since_update + data_length
                    data = None
                    data_length = 0
                    if bytes_since_update > self.update_threshold:
                        self.update_progress_bar()
                        bytes_since_update = 0

                except (socket.timeout, socket.error) as e:
                    if isinstance(e, socket.timeout):
                        break
                    elif isinstance(e, socket.error):
                        errorcode = e[0]
                        if errorcode == errno.EINTR:
                            pass
                        else:
                            self.cleanup()
                            raise
                    else:
                        self.cleanup()
                        raise

        self.cleanup()
        self.logger.info('{}: download complete: {}'.format(self.remote_host,
                                                            filename))

    def to_s3(self, key_id, secret_key, bucket, filename):
        if self.draw_pbar:
            self.pbar = ProgressBar(widgets=self.widgets,
                                    maxval=self.maxsize).start()
            self.pbar.start()
            pbar_update = True

        s3 = s3fs.S3FileSystem(anon=False,
                               key=key_id,
                               secret=secret_key)
        with s3.open('{}/{}'.format(bucket, filename), 'wb') as self.outfile:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.tunnel_host, self.tunnel_port))
            self.sock.settimeout(self.sock_timeout)
            bytes_since_update = 0

            while True:
                try:
                    data = self.sock.recv(self.recv_size)
                    data_length = len(data)
                    if not data:
                        break
                    self.outfile.write(data)
                    self.transfered = self.transfered + data_length
                    bytes_since_update = bytes_since_update + data_length
                    data = None
                    data_length = 0
                    self.update_progress_bar()
                    if bytes_since_update > self.update_threshold:
                        self.update_progress_bar()
                        bytes_since_update = 0

                except (socket.timeout, socket.error, select.error) as e:
                    if isinstance(e, socket.timeout):
                        break
                    elif isinstance(e, socket.error):
                        errorcode = e[0]
                        if errorcode == errno.EINTR:
                            pass
                        else:
                            self.cleanup()
                            raise
                    elif isinstance(e, select.error):
                        errorcode = e[0]
                        if errorcode == errno.EINTR:
                            pass
                        else:
                            self.cleanup()
                            raise
                    else:
                        self.cleanup()
                        raise

        self.cleanup()
        self.logger.info('Upload complete: {}'.format(filename))

    def cleanup(self):
        self.sock.close()
        self.outfile.close()
        self.update_progress_bar(complete=True)
