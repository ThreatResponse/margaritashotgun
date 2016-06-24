import datetime
import requests
import xmltodict
import logging

logger = logging.getLogger(__name__)

class Repository():
    """
    """

    # TODO: prompt asking the user if they would like to check for modules?
    def __init__(self, url="https://s3.amazonaws.com/lime-modules/"):
        """
        """
        self.url = url

    def search_modules(self, kernel_version):
        """
        """
        self.kernel_version = kernel_version
        manifest = self.list_modules()
        # TODO: standardize keys?
        # TODO: allow setting patter for keys
        key = "{0}.ko".format(kernel_version)
        alt_key = "lime-{0}.ko".format(kernel_version)
        # TODO allow prompting the user to select multiple matches
        match = None
        if manifest is not None:
            for entry in manifest:
                entry_key = entry['Key']
                if key == entry_key or alt_key == entry_key:
                    match = entry_key
        return match

    def list_modules(self):
        """
        """
        req = requests.get(self.url)
        if req.status_code is 200:
            data = req.text
        else:
            # TODO: handle differnetly
            return None
        try:
            manifest = xmltodict.parse(data)
            return manifest['ListBucketResult']['Contents']
        # TODO: handle specific exceptions
        # TODO: handle different exception for dictionary key errors
        except Exception as ex:
            # TODO: log an error and raise the exception
            return None

    def fetch_module(self, urn, filename=None, chunk_size=4096, verify=False):
        """
        """
        if filename is None:
            datestamp = datetime.datetime.now().isoformat()
            filename = "lime-{0}-{1}.ko".format(datestamp, self.kernel_version)
        url = self.url + urn
        req = requests.get(url, stream=True)

        with open(filename, 'w') as f:
            for chunk in req.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(str(chunk))

        # TODO: verify file agains gpg key here

        return filename

    def verify_module_signature(self):
        """
        """
        print('todo')
        return True
