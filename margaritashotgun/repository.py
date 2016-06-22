import logging

logger = logging.getLogger(__name__)

class Repository():
    """
    """

    def __init__(self):
        print('init')

    def get_kernel_module(self):
        print('todo')
#    def get_kernel_module(self, bucket_path="lime-modules"):
#        kernel_version = self.get_kernel_version()
#        self.logger.info("{} kernel version: {}".format(self.address,
#                                                        kernel_version))
#        mod = self.match_kernel_module(kernel_version)
#        if mod[0] is False:
#            self.logger.info("No Matching Lime Module Found")
#            return (None, kernel_version)
#        else:
#            url = "{}/{}/{}".format(self.s3_prefix, bucket_path, mod[1]['Key'])
#            req = requests.get(url, stream=True)
#            datestamp = datetime.datetime.now().isoformat()
#            filename = "lime_download_{}_{}.ko".format(kernel_version,
#                                                       datestamp)
#            self.logger.info("downloading {} as {}".format(url, filename))
#            try:
#                with open(filename, 'w') as f:
#                    for chunk in req.iter_content(chunk_size=4096):
#                        if chunk:
#                            f.write(str(chunk))
#            except IOError as e:
#                self.logger.info("Error fetching lime module: {}".format(
#                                 str(e)))
#                raise
#
#            if self.verify_kernel_module(filename, url) is False:
#                raise LimeError('signature check failed for {}'.format(
#                                filename))
#            return (filename, kernel_version)

    def match_kernel_module(self):
        print('todo')

#    def match_kernel_module(self, kernel_version):
#        manifest = self.enumerate_kernel_modules()
#        lime_key = "{}.ko".format(kernel_version)
#        lime_key_alt = "lime-{}.ko".format(kernel_version)
#        ret = None
#        for entry in manifest:
#            if lime_key == entry['Key'] or lime_key_alt == entry['Key']:
#                ret = (True, entry)
#                break
#        if ret is None:
#            ret = (False, None)
#        return ret

#    def enumerate_kernel_modules(self, bucket_path="lime-modules"):
#        req = requests.get("https://s3.amazonaws.com/{}/".format(bucket_path))
#        if req.status_code is 200:
#            data = req.text
#        else:
#            self.logger.info("Cannot enumerate lime module repository")
#        try:
#            manifest = xmltodict.parse(data)
#        except Exception as e:
#            self.logger.info("Error parsing repository listing {}".format(e))
#        return manifest['ListBucketResult']['Contents']




