import multiprocessing
from multiprocessing import Pool
from margaritashotgun import remote_host
import logging

#????
import signal

logger = logging.getLogger(__name__)

class Workers():
    """
    """
    cpu_count = None
    worker_count = None
    progress_bar = True
    hosts = None

    def __init__(self, conf, workers, library=True):
        """
        """
        # TODO: parameterize this
        self.library = library
        self.progressbar = True
        self.cpu_count = multiprocessing.cpu_count()
        host_count = len(conf)
        self.worker_count = self.count(workers, self.cpu_count, host_count)
        if self.worker_count > 1 or self.library is True:
            self.progressbar = False
        self.conf = []
        for c in conf:
            c['host']['progressbar'] = self.progressbar
            self.conf.append(c)

    def count(self, workers, cpu_count, host_count):
        """
        """
        if workers == 'auto':
            worker_count = cpu_count
        elif workers > host_count:
            worker_count = host_count
        else:
            worker_count = int(workers)
        return worker_count

    # TODO: support configuring the memory capture timeout
    def spawn(self, timeout=1800):
        """
        """
        pool = Pool(self.worker_count)
        res = pool.map_async(remote_host.process, self.conf)
        results = res.get(500)
        pool.close()
        pool.join()
        return results
