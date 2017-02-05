from progressbar import ProgressBar, Percentage, Bar, ETA, FileTransferSpeed
from enum import Enum
import errno
import select
import socket
import s3fs
import logging
from margaritashotgun.exceptions import *

logger = logging.getLogger(__name__)


class OutputDestinations(Enum):
    local = 'local'
    s3 = 's3'


class Memory():

    def __init__(self, remote_addr, mem_size, progressbar=False,
                 recv_size=1048576, sock_timeout=1):
        """
        :type remote_addr: str
        :param remote_addr: hostname or ip address of target server
        :type mem_size: int
        :param mem_size: target server memory size in bytes
        :type progressbar: bool
        :param progressbar: ncurses progress bar toggle
        :type recv_size: int
        :param recv_size: transfer socket max receive size
        :type sock_timeout: int
        :param sock_timeout: transfer socket receive timeout
        """
        self.mem_size = mem_size
        self.progressbar = progressbar
        self.recv_size = recv_size
        self.sock_timeout = sock_timeout
        self.padding_percentage = 0.03
        self.max_size = self.max_size(mem_size, self.padding_percentage)
        self.update_interval = 5
        self.update_threshold = recv_size * self.update_interval
        self.remote_addr = remote_addr
        self.transfered = 0
        self.progress = 0
        self.widgets = [' {0} '.format(remote_addr), Percentage(), ' ', Bar(),
                        ' ', ETA(), ' ', FileTransferSpeed()]
        self.sock = None
        self.outfile = None
        self.bar = None

    def max_size(self, mem_size, padding_percentage):
        """
        Calculates the excpected size in bytes of the memory capture

        :type mem_size: int
        :param mem_size: target server memory in bytes
        :type padding_percentage: float
        :param padding_percentage: Output overhead of lime format
        """
        size_in_kb = mem_size + mem_size * padding_percentage
        return size_in_kb * 1024

    def capture(self, tunnel_addr, tunnel_port, filename=None,
                bucket=None, destination=None):
        """
        Captures memory based on the provided OutputDestination

        :type tunnel_addr: str
        :param tunnel_port: ssh tunnel hostname or ip
        :type tunnel_port: int
        :param tunnel_port: ssh tunnel port
        :type filename: str
        :param filename: memory dump output filename
        :type bucket: str
        :param bucket: output s3 bucket
        :type destination: :py:class:`margaritashotgun.memory.OutputDestinations`
        :param destination: OutputDestinations member
        """
        if filename is None:
            raise MemoryCaptureAttributeMissingError('filename')
        if destination == OutputDestinations.local:
            logger.info("{0}: dumping to file://{1}".format(self.remote_addr,
                                                            filename))
            result = self.to_file(filename, tunnel_addr, tunnel_port)
        elif destination == OutputDestinations.s3:
            if bucket is None:
                raise MemoryCaptureAttributeMissingError('bucket')
            logger.info(("{0}: dumping memory to s3://{1}/"
                         "{2}".format(self.remote_addr, bucket, filename)))
            result = self.to_s3(bucket, filename, tunnel_addr, tunnel_port)
        else:
            raise MemoryCaptureOutputMissingError(self.remote_addr)

        return result

    def to_file(self, filename, tunnel_addr, tunnel_port):
        """
        Writes memory dump to a local file

        :type filename: str
        :param filename: memory dump output filename
        :type tunnel_addr: str
        :param tunnel_port: ssh tunnel hostname or ip
        :type tunnel_port: int
        :param tunnel_port: ssh tunnel port
        """
        if self.progressbar:
            self.bar = ProgressBar(widgets=self.widgets,
                                   maxval=self.max_size).start()
            self.bar.start()

        with open(filename, 'wb') as self.outfile:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((tunnel_addr, tunnel_port))
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
                    bytes_since_update +=  data_length
                    data = None
                    data_length = 0
                    if bytes_since_update > self.update_threshold:
                        self.update_progress()
                        bytes_since_update = 0

                except (socket.timeout, socket.error) as ex:
                    if isinstance(ex, socket.timeout):
                        break
                    elif isinstance(ex, socket.error):
                        if ex.errno == errno.EINTR:
                            pass
                        else:
                            self.cleanup()
                            raise
                    else:
                        self.cleanup()
                        raise

        self.cleanup()
        logger.info('{0}: capture complete: {1}'.format(self.remote_addr,
                                                        filename))
        return True

    def to_s3(self, bucket, filename, tunnel_addr, tunnel_port):
        """
        Writes memory dump to s3 bucket

        :type bucket: str
        :param bucket: memory dump output s3 bucket
        :type filename: str
        :param filename: memory dump output filename
        :type tunnel_addr: str
        :param tunnel_port: ssh tunnel hostname or ip
        :type tunnel_port: int
        :param tunnel_port: ssh tunnel port
        """
        if self.progressbar:
            self.bar = ProgressBar(widgets=self.widgets,
                                   maxval=self.max_size).start()
            self.bar.start()

        s3 = s3fs.S3FileSystem(anon=False)
        with s3.open('{0}/{1}'.format(bucket, filename), 'wb') as self.outfile:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((tunnel_addr, tunnel_port))
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
                        self.update_progress()
                        bytes_since_update = 0

                except (socket.timeout, socket.error, select.error) as ex:
                    if isinstance(ex, socket.timeout):
                        break
                    elif isinstance(ex, socket.error):
                        if ex.errno == errno.EINTR:
                            pass
                        else:
                            self.cleanup()
                            raise
                    elif isinstance(ex, select.error):
                        if ex.errno == errno.EINTR:
                            pass
                        else:
                            self.cleanup()
                            raise
                    else:
                        self.cleanup()
                        raise
        self.cleanup()
        logger.info('{0}: capture complete: s3://{1}/{2}'.format(self.remote_addr,
                                                                 bucket,
                                                                 filename))
        return True

    def update_progress(self, complete=False):
        """
        Logs capture progress

        :type complete: bool
        :params complete: toggle to finish ncurses progress bar
        """
        if self.progressbar:
            try:
                self.bar.update(self.transfered)
            except Exception as e:
                logger.debug("{0}: {1}, {2} exceeds memsize {3}".format(
                                 self.remote_addr,
                                 e,
                                 self.transfered,
                                 self.max_size))
            if complete:
                self.bar.update(self.max_size)
                self.bar.finish()
        else:
            percent = int(100 * float(self.transfered) / float(self.max_size))
            # printe a message at 10%, 20%, etc...
            if percent % 10 == 0:
                if self.progress != percent:
                    logger.info("{0}: capture {1}% complete".format(
                                self.remote_addr, percent))
                    self.progress = percent

    def cleanup(self):
        """
        Release resources used during memory capture
        """
        if self.sock is not None:
            self.sock.close()
        if self.outfile is not None:
            self.outfile.close()
        if self.bar is not None:
            self.update_progress(complete=True)
