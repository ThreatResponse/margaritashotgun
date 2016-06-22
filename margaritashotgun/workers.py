import multiprocessing
from multiprocessing import Pool
import margaritashotgun.remote_host
import logging

logger = logging.getLogger(__name__)


class Workers():
    """
    """
    cpu_count = None
    worker_count = None
    progress_bar = True
    hosts = None

    def __init__(self, hosts, workers, library=True):
        """
        """

        hosts = hosts
        cpu_count = multiprocessing.cpu_count()
        host_count = len(hosts)
        worker_count = self.count(workers, cpu_count, host_count)
        if worker_count > 1 or library is True:
            progress_bar = False

        hosts = [host['progress_bar'] = progress_bar for host in hosts]

    def count(self, workers, cpu_count, host_count):
        """
        """
        if workers == 'auto':
            worker_count = cpu_count
        if workers > host_count:
            worker_count = host_count
        else:
            worker_count = int(workers)
        return worker_count

    def spawn(self):
        """
        """
        print("todo")
        return 0
        # for later
        pool = Pool(worker_count)
        results = pool.map(func, hosts)
        pool.close()
        pool.join()
        return results

