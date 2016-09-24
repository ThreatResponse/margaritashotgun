import gzip
import hashlib
import logging
import requests
import time
import untangle
from datetime import datetime
from StringIO import StringIO
from margaritashotgun.exceptions import *

logger = logging.getLogger(__name__)


class Repository():
    """
    """

    def __init__(self, url, gpg_verify):
        """
        """
        self.url = url.rstrip('/')
        self.gpg_verify = gpg_verify
        self.metadata_dir = 'repodata'
        self.metadata_file = 'repomd.xml'

    def fetch(self, kernel_version, manifest_type):
        """
        """
        metadata = self.get_metadata()
        logger.debug("parsed metadata: {0}".format(metadata))
        manifest = self.get_manifest(metadata['manifests'][manifest_type])

        try:
            module = manifest[kernel_version]
            logger.debug("found module {0}".format(module))
        except KeyError:
            raise KernelModuleNotFoundError(kernel_version, self.url)
        path = self.fetch_module(module, verify_signature = self.gpg_verify)

        return path

    def get_metadata(self):
        """
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
        """
        buf = StringIO(raw_manifest)
        f = gzip.GzipFile(fileobj=buf)
        manifest = f.read()

        return manifest

    def parse_manifest(self, manifest_xml):
        """
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

    def fetch_module(self, module, filename=None, verify_signature=False):
        """
        """
        if filename is None:
            tm = int(time.time())
            datestamp = datetime.utcfromtimestamp(tm).isoformat()
            filename = "lime-{0}-{1}.ko".format(datestamp, module['version'])
        url = "{0}/{1}".format(self.url, module['location'])
        logger.info("downloading {0} as {1}".format(url, filename))
        req = requests.get(url, stream=True)

        with open(filename, 'wb') as f:
            f.write(req.raw.read())

        self.verify_module(filename, module, verify_signature)
        return filename

    def verify_module(self, filename, module, verify_signature):
        """
        """
        with open(filename, 'rb') as f:
            module_data = f.read()
        self.verify_checksum(module_data, module['checksum'],
                             module['location'])

        #TODO: verify gpg signature


    def verify_checksum(self, data, checksum, filename):
        calculated_checksum = hashlib.sha256(data).hexdigest()
        logger.debug("calculated checksum {0} for {1}".format(calculated_checksum,
                                                              filename))
        if calculated_checksum != checksum:
            raise RepositoryError("{0}/{1}".format(self.url, filename),
                                  ("checksum verification failed, expected "
                                   "{0} got {1}".format(checksum,
                                                        calculated_checksum)))

    def verify_signature(self):
        # TODO: verify gpg signature
        return True
