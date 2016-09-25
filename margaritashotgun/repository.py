import gnupg
import gzip
import hashlib
import logging
import os
import requests
import time
import untangle
from datetime import datetime
from StringIO import StringIO
from margaritashotgun.exceptions import *
from prompt_toolkit import prompt

logger = logging.getLogger(__name__)


class Repository():
    """
    Lime-compiler repository client
    https://github.com/ThreatResponse/lime-compiler
    """

    def __init__(self, url, gpg_verify):
        """
        :type url: str
        :param url: repository url
        :type gpg_verify: bool
        :param gpg_verify: enable/disable gpg signature verification
        """
        self.url = url.rstrip('/')
        self.gpg_verify = gpg_verify
        self.metadata_dir = 'repodata'
        self.metadata_file = 'repomd.xml'
        self.repo_signing_key = 'REPO_SIGNING_KEY.asc'

        self.gpg = None
        self.key_path = None
        self.key_info = None
        self.raw_key = None

    def init_gpg(self):
        """
        Initialize gpg object and check if repository signing key is trusted
        """
        if self.gpg_verify:
            logger.debug("gpg verification enabled, initializing gpg")
            gpg_home = os.path.expanduser('~/.gnupg')
            self.gpg = gnupg.GPG(gnupghome=gpg_home)
            self.key_path, self.key_info = self.get_signing_key()
            logger.debug("{0} {1}".format(self.key_path, self.key_info))
            self.check_signing_key()

    def get_signing_key(self):
        """
        Download a local copy of repo signing key and generate key metadata
        """
        tmp_path = "/tmp/{0}".format(self.repo_signing_key)
        repo_key_path = "{0}/{1}".format(self.url, self.repo_signing_key)
        req = requests.get(repo_key_path)
        if req.status_code is 200:
            logger.debug(("found repository signing key at "
                         "{0}".format(repo_key_path)))
            self.raw_key = req.content
            with open(tmp_path, 'wb') as f:
                f.write(self.raw_key)
            key_info = self.gpg.scan_keys(tmp_path)
            # we only scan one key, return a single key_info
            key_info = key_info[0]
        else:
            raise RepositoryMissingSigningKeyError(repo_key_path)
        return (tmp_path, key_info)

    def check_signing_key(self):
        """
        Check that repo signing key is trusted by gpg keychain
        """
        user_keys = self.gpg.list_keys()
        if len(user_keys) > 0:
            trusted = False
            for key in user_keys:
                if key['fingerprint'] == self.key_info['fingerprint']:
                    trusted = True
                    logger.debug(("repo signing key trusted in user keyring, "
                                  "fingerprint {0}".format(key['fingerprint'])))
        else:
            trusted = False
        if trusted is False:
            repo_key_url = "{0}/{1}".format(self.url, self.repo_signing_key)
            raise RepositoryUntrustedSigningKeyError(repo_key_url,
                                                     self.key_info['fingerprint'])

    def prompt_for_install(self):
        """
        Prompt user to install untrusted repo signing key
        """
        print(self.key_info)
        repo_key_url = "{0}/{1}".format(self.url, self.repo_signing_key)
        print(("warning: Repository key untrusted \n"
               "Importing GPG key 0x{0}:\n"
               "  Userid: \"{1}\"\n"
               "  From  : {2}".format(self.key_info['fingerprint'],
                                      self.key_info['uids'][0],
                                      repo_key_url)))
        response = prompt(u'Is this ok: [y/N]')
        if response == 'y':
            self.install_key(self.raw_key)
            return True
        else:
            return False

    def install_key(self, key_data):
        """
        Install untrusted repo signing key
        """
        logger.info(("importing repository signing key {0} "
                     "{1}".format(self.key_info['fingerprint'],
                                  self.key_info['uids'][0])))
        import_result = self.gpg.import_keys(key_data)
        logger.debug("import results: {0}".format(import_result.results))

    def fetch(self, kernel_version, manifest_type):
        """
        Search repository for kernel module matching kernel_version

        :type kernel_version: str
        :param kernel_version: kernel version to search repository on
        :type manifest_type: str
        :param manifest_type: kernel module manifest to search on
        """
        metadata = self.get_metadata()
        logger.debug("parsed metadata: {0}".format(metadata))
        manifest = self.get_manifest(metadata['manifests'][manifest_type])

        try:
            module = manifest[kernel_version]
            logger.debug("found module {0}".format(module))
        except KeyError:
            raise KernelModuleNotFoundError(kernel_version, self.url)
        path = self.fetch_module(module)

        return path

    def get_metadata(self):
        """
        Fetch repository repomd.xml file
        """
        metadata_path = "{}/{}/{}".format(self.url,
                                          self.metadata_dir,
                                          self.metadata_file)
        metadata_sig_path = "{}/{}/{}.sig".format(self.url.rstrip('/'),
                                                  self.metadata_dir,
                                                  self.metadata_file)
        # load metadata
        req = requests.get(metadata_path)
        if req.status_code is 200:
            raw_metadata = req.content
        else:
            raise RepositoryError(metadata_path, ("status code not 200: "
                                                  "{}".format(req.status_code)))

        # load metadata signature
        if self.gpg_verify:
            req = requests.get(metadata_sig_path)
            if req.status_code is 200:
                signature = req.content
            else:
                raise RepositoryError(metadata_sig_path,
                                      ("status code not 200: "
                                       "{}".format(req.status_code)))

        # TODO: verify gpg signature

        return self.parse_metadata(raw_metadata)

    def parse_metadata(self, metadata_xml):
        """
        Parse repomd.xml file

        :type metadata_xml: str
        :param metadata_xml: raw xml representation of repomd.xml
        """
        try:
            metadata = dict()
            mdata = untangle.parse(metadata_xml).metadata
            metadata['revision'] = mdata.revision.cdata
            metadata['manifests'] = dict()

            # check if multiple manifests are present
            if type(mdata.data) is list:
                manifests = mdata.data
            else:
                manifests = [mdata.data]

            for manifest in manifests:
                manifest_dict = dict()
                manifest_dict['type'] = manifest['type']
                manifest_dict['checksum'] = manifest.checksum.cdata
                manifest_dict['open_checksum'] = manifest.open_checksum.cdata
                manifest_dict['location'] = manifest.location['href']
                manifest_dict['timestamp'] = datetime.fromtimestamp(
                                                 int(manifest.timestamp.cdata))
                manifest_dict['size'] = int(manifest.size.cdata)
                manifest_dict['open_size'] = int(manifest.open_size.cdata)
                metadata['manifests'][manifest['type']] = manifest_dict

        except Exception as e:
            raise RepositoryError("{0}/{1}".format(self.url,self.metadata_dir,
                                                   self.metadata_file), e)

        return metadata

    def get_manifest(self, metadata):
        """
        Get latest manifest as specified in repomd.xml

        :type metadata: dict
        :param metadata: dictionary representation of repomd.xml
        """
        manifest_path = "{0}/{1}".format(self.url, metadata['location'])
        req = requests.get(manifest_path, stream=True)
        if req.status_code is 200:
            gz_manifest = req.raw.read()

        self.verify_checksum(gz_manifest, metadata['checksum'],
                             metadata['location'])
        manifest = self.unzip_manifest(gz_manifest)
        self.verify_checksum(manifest, metadata['open_checksum'],
                             metadata['location'].rstrip('.gz'))

        return self.parse_manifest(manifest)

    def unzip_manifest(self, raw_manifest):
        """
        Decompress gzip encoded manifest

        :type raw_manifest: str
        :param raw_manifest: compressed gzip manifest file content
        """
        buf = StringIO(raw_manifest)
        f = gzip.GzipFile(fileobj=buf)
        manifest = f.read()

        return manifest

    def parse_manifest(self, manifest_xml):
        """
        Parse manifest xml file

        :type manifest_xml: str
        :param manifest_xml: raw xml content of manifest file
        """

        manifest = dict()
        try:
            mdata = untangle.parse(manifest_xml).modules
            for module in mdata.children:
                mod = dict()
                mod['type'] = module['type']
                mod['name'] = module.name.cdata
                mod['arch'] = module.arch.cdata
                mod['checksum'] = module.checksum.cdata
                mod['version'] = module.version.cdata
                mod['packager'] = module.packager.cdata
                mod['location'] = module.location['href']
                mod['signature'] = module.signature['href']
                mod['platform'] = module.platform.cdata
                manifest[mod['version']] = mod

        except Exception as e:
            print(e)

        return manifest

    def fetch_module(self, module):
        """
        Download and verify kernel module

        :type module: str
        :param module: kernel module path
        """
        tm = int(time.time())
        datestamp = datetime.utcfromtimestamp(tm).isoformat()
        filename = "lime-{0}-{1}.ko".format(datestamp, module['version'])
        url = "{0}/{1}".format(self.url, module['location'])
        logger.info("downloading {0} as {1}".format(url, filename))
        req = requests.get(url, stream=True)

        with open(filename, 'wb') as f:
            f.write(req.raw.read())

        self.verify_module(filename, module, self.gpg_verify)
        return filename

    def verify_module(self, filename, module, verify_signature):
        """
        Verify kernel module checksum and signature

        :type filename: str
        :param filename: downloaded kernel module path
        :type module: dict
        :param module: kernel module metadata
        :type verify_signature: bool
        :param verify_signature: enable/disable signature verification
        """
        with open(filename, 'rb') as f:
            module_data = f.read()
        self.verify_checksum(module_data, module['checksum'],
                             module['location'])

        #TODO: verify gpg signature


    def verify_checksum(self, data, checksum, filename):
        """
        Verify sha256 checksum vs calculated checksum

        :type data: str
        :param data: data used to calculate checksum
        :type checksum: str
        :param checksum: expected checksum of data
        :type filename: str
        :param checksum: original filename
        """
        calculated_checksum = hashlib.sha256(data).hexdigest()
        logger.debug("calculated checksum {0} for {1}".format(calculated_checksum,
                                                              filename))
        if calculated_checksum != checksum:
            raise RepositoryError("{0}/{1}".format(self.url, filename),
                                  ("checksum verification failed, expected "
                                   "{0} got {1}".format(checksum,
                                                        calculated_checksum)))

    def verify_signature(self):
        """
        """
        # TODO: verify gpg signature
        return True
