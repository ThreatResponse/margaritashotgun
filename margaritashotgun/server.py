#!/usr/bin/env python

import datetime
import paramiko
import threading
import time
import requests
import xmltodict
from .limeerror import limeerror as LimeError


class server():
    def __init__(self, address, port, username, logger, verbose=False):
        self.ssh = paramiko.SSHClient()
        self.address = address
        self.port = port
        self.username = username
        self.verbose = verbose
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.s3_prefix = "https://s3.amazonaws.com"
        self.logger = logger

    def connect_with_password(self, password):
        self.ssh.connect(hostname=self.address,
                         port=self.port,
                         username=self.username,
                         password=password)

    def connect_with_keyfile(self, private_key_path):
        key = paramiko.RSAKey.from_private_key_file(private_key_path)
        self.ssh.connect(hostname=self.address,
                         port=self.port,
                         username=self.username,
                         pkey=key)

    def connect_with_encrypted_keyfile(self, private_key_path, password):
        key = paramiko.RSAKey.from_private_key_file(private_key_path,
                                                    password=password)
        self.ssh.connect(hostname=self.address,
                         port=self.port,
                         username=self.username,
                         pkey=key)

    def test_conn(self):
        try:
            stdin, stdout, stderr = self.ssh.exec_command('ls -a')
            if stdin is not None:
                connection_status = True
            else:
                connection_status = False
        # TODO: (joel) use specific exceptions
        except Exception as e:
            connection_status = False
        return connection_status

    def get_mem_size(self):
        stdin, stdout, stderr = self.ssh.exec_command(
            "cat /proc/meminfo | grep MemTotal | awk '{ print $2 }'")
        for line in stdout:
            memsize = int(line.strip('\n'))
        return memsize*1024  # convert from Kb to bytes

    def get_kernel_version(self):
        stdin, stdout, stderr = self.ssh.exec_command("uname -r")
        output = stdout.readline()
        return output.rstrip()

    def get_kernel_module(self, bucket_path="lime-modules"):
        kernel_version = self.get_kernel_version()
        self.logger.info("{} kernel version: {}".format(self.address,
                                                        kernel_version))
        mod = self.match_kernel_module(kernel_version)
        if mod[0] is False:
            self.logger.info("No Matching Lime Module Found")
            return (None, kernel_version)
        else:
            url = "{}/{}/{}".format(self.s3_prefix, bucket_path, mod[1]['Key'])
            req = requests.get(url, stream=True)
            datestamp = datetime.datetime.now().isoformat()
            filename = "lime_download_{}_{}.ko".format(kernel_version, datestamp)
            self.logger.info("downloading {} as {}".format(url, filename))
            try:
                with open(filename, 'w') as f:
                    for chunk in req.iter_content(chunk_size=4096):
                        if chunk:
                            f.write(str(chunk))
            except IOError as e:
                self.logger.info("Error fetching lime module: {}".format(str(e)))
                raise

            if self.verify_kernel_module(filename, url) is False:
                raise LimeError('signature check failed for {}'.format(filename))
            return (filename, kernel_version)

    def match_kernel_module(self, kernel_version):
        manifest = self.enumerate_kernel_modules()
        lime_key = "{}.ko".format(kernel_version)
        lime_key_alt = "lime-{}.ko".format(kernel_version)
        ret = None
        for entry in manifest:
            if lime_key == entry['Key'] or lime_key_alt == entry['Key']:
                ret = (True, entry)
                break
        if ret is None:
            ret = (False, None)
        return ret

    def enumerate_kernel_modules(self, bucket_path="lime-modules"):
        req = requests.get("https://s3.amazonaws.com/{}/".format(bucket_path))
        if req.status_code is 200:
            data = req.text
        else:
            self.logger.info("Cannot enumerate lime module repository")
        try:
            manifest = xmltodict.parse(data)
        except Exception as e:
            self.logger.info("Error parsing repository listing {}".format(e))
        return manifest['ListBucketResult']['Contents']

    # TODO: (joel) verify signatures on downloaded files
    def verify_kernel_module(self, file_name, download_url):
        return True

    def wait_for_lime(self, port=4000):
        tries = 0
        lime_listener = "0.0.0.0:{}".format(port)
        command = "netstat -lnt | grep {}".format(port)
        lime_loaded = False
        while tries < 60 and lime_loaded is False:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            output = stdout.read().decode('utf-8').strip("\n")
            if lime_listener in output:
                lime_loaded = True
            tries = tries + 1
            time.sleep(1)
        return lime_loaded

    def upload_file(self, local_path, remote_path):
        sftp = self.ssh.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()

    def execute(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        if self.verbose:
            for line in stdout:
                self.logger.verbose("{} cmd:{}".format(self.address,
                                                       line.strip('\n')))

    def execute_async(self, command):
        worker = async_worker(command, self.ssh)
        worker.start()

    def cleanup(self):
        self.ssh.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.ssh.close()


class async_worker(threading.Thread):

    def __init__(self, command, ssh):
        super(async_worker, self).__init__()
        self.command = command
        self.ssh = ssh

    def run(self):
        stdin, stdout, stderr = self.ssh.exec_command(self.command, timeout=60)
