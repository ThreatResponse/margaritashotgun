import multiprocessing
from multiprocessing import Pool
from margaritashotgun import remote_host
from margaritashotgun import logger
import logging


def _init(queue):
    global log_queue
    log_queue = queue


class Workers():
    """
    """
    cpu_count = None
    worker_count = None
    progress_bar = True
    hosts = None

    def __init__(self, conf, workers, name, library=True):
        """
        """
        self.name = name
        self.library = library
        self.progressbar = True
        self.cpu_count = multiprocessing.cpu_count()
        host_count = len(conf)
        self.worker_count = self.count(workers, self.cpu_count, host_count)
        self.log_file = "{}{}margaritashotgun_actions.log".format(
                            conf[0]['logging']['log_dir'],
                            conf[0]['logging']['prefix'])
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

    def spawn(self, timeout=1800):
        """
        """
        #TODO: move queue to argument? # -1 is queue maxsize
        queue = multiprocessing.Queue(-1)
        pool = Pool(self.worker_count, initializer=remote_host._init, initargs=(queue,))
        # setup logging listener
        listener = logger.Logger(target=logger.listener, args=(queue, self.name, self.log_file))
        listener.start()
        res = pool.map_async(remote_host.process, self.conf)
        results = res.get(timeout)
        pool.close()
        pool.join()
        queue.put_nowait(None)
        listener.join()
        return results
