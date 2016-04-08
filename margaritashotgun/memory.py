#!/usr/bin/env python

from progressbar import ProgressBar, Percentage, Bar, ETA, FileTransferSpeed
import socket
import s3fs

class memory():

    def __init__(self, remote_host, remote_port, memsize):
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.recv_size   = 1024*1024
        self.memsize     = memsize
        padding          = memsize * 0.03
        self.maxsize     = memsize + padding # pad filesize by 3% to account for lime memdump format
        self.transfered  = 0
        self.widgets     = [Percentage(), ' ', Bar(), ' ', ETA(), ' ', FileTransferSpeed()]

    def to_file(self, filename):
        pbar = ProgressBar(widgets=self.widgets, maxval=self.maxsize).start()
        pbar.start()
        pbar_update = True

        with open(filename, 'wb') as outfile:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.remote_host, self.remote_port))
            while True:
                data = sock.recv(self.recv_size)
                if not data:
                    break
                outfile.write(data)
                self.transfered = self.transfered + len(data)
                # this is awful
                try:
                    if pbar_update == True:
                        pbar.update(self.transfered)
                except Exception as e:
                    pbar_update = False
                    print("{}: {} exceeds memsize {}".format(e, self.transfered, self.maxsize))
            sock.close()
            outfile.close()
            if pbar_update == True:
                pbar.update(self.maxsize)
                pbar.finish()
        print('Download complete: {}'.format(filename))

    def to_s3(self, key_id, secret_key, bucket, filename):
        pbar = ProgressBar(widgets=self.widgets, maxval=self.maxsize).start()
        pbar.start()
        pbar_update = True

        s3 = s3fs.S3FileSystem(anon=False,
                               key=key_id,
                               secret=secret_key)
        with s3.open('{}/{}'.format(bucket, filename), 'wb') as outfile:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.remote_host, self.remote_port))

            while True:
                data = sock.recv(self.recv_size)
                if not data:
                    break
                outfile.write(data)
                self.transfered = self.transfered + len(data)
                try:
                    if pbar_update == True:
                        pbar.update(self.transfered)
                except Exception as e:
                    update = False
                    #TODO: (joel) add verbose check
                    #print("{}: {} exceeds memsize {}".format(e, self.transfered, self.maxval))
        if pbar_update == True:
            pbar.update(self.maxsize)
            pbar.finish()
        print('Upload complete: {}/{}'.format(bucket,filename))

