#!/usr/bin/env python

from progressbar import ProgressBar, Percentage, Bar, ETA, FileTransferSpeed
import errno
import select
import socket
import s3fs


class memory():

    def __init__(self, remote_host, remote_port, memsize, logger,
                 recv_size=1048576, sock_timeout=2):
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.recv_size = recv_size
        self.memsize = memsize
        padding = memsize * 0.03
        self.maxsize = memsize + padding
        self.transfered = 0
        self.widgets = [Percentage(), ' ', Bar(), ' ', ETA(), ' ',
                        FileTransferSpeed()]
        self.sock_timeout = sock_timeout
        self.logger = logger

    def to_file(self, filename):
        self.pbar = ProgressBar(widgets=self.widgets,
                                maxval=self.maxsize).start()
        self.pbar.start()
        pbar_update = True

        with open(filename, 'wb') as self.outfile:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.remote_host, self.remote_port))
            self.sock.settimeout(self.sock_timeout)
            while True:
                try:
                    data = self.sock.recv(self.recv_size)
                    data_length = len(data)
                    if not data:
                        break
                    self.outfile.write(data)
                    self.transfered = self.transfered + data_length
                    data = None
                    data_length = 0
                    try:
                        self.pbar.update(self.transfered)
                    except Exception as e:
                        self.logger.info("{}: {} exceeds memsize {}".format(
                                         e,
                                         self.transfered,
                                         self.maxsize))

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
        self.logger.info('Download complete: {}'.format(filename))

    def to_s3(self, key_id, secret_key, bucket, filename):
        self.pbar = ProgressBar(widgets=self.widgets,
                                maxval=self.maxsize).start()
        self.pbar.start()
        pbar_update = True

        s3 = s3fs.S3FileSystem(anon=False,
                               key=key_id,
                               secret=secret_key)
        with s3.open('{}/{}'.format(bucket, filename), 'wb') as self.outfile:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.remote_host, self.remote_port))
            self.sock.settimeout(self.sock_timeout)

            while True:
                try:
                    data = self.sock.recv(self.recv_size)
                    data_length = len(data)
                    if not data:
                        break
                    self.outfile.write(data)
                    self.transfered = self.transfered + data_length
                    data = None
                    data_length = 0
                    try:
                        self.pbar.update(self.transfered)
                    except Exception as e:
                        self.logger.info("{}: {} exceeds memsize {}".format(
                                         e,
                                         self.transfered,
                                         self.maxval))
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
        self.pbar.update(self.maxsize)
        self.pbar.finish()
