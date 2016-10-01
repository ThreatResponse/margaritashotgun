import multiprocessing
from multiprocessing import Pool
from margaritashotgun import remote_host
from margaritashotgun import logger
import logging


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
        self.queue = multiprocessing.Queue(-1)

        try:
            log_dir = conf[0]['logging']['dir']
            if log_dir[-1:] != '/':
                log_dir = log_dir + '/'
        except TypeError:
            log_dir = ""
        try:
            log_prefix = conf[0]['logging']['prefix'] + "-"
        except TypeError:
            log_prefix = ""

        self.log_file = "{}{}memory-capture.log".format(
                            log_dir, log_prefix)

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
            if cpu_count > host_count:
                worker_count = host_count
            else:
                worker_count = cpu_count
        elif workers > host_count:
            worker_count = host_count
        else:
            worker_count = int(workers)
        return worker_count

    def spawn(self, desc, timeout=1800):
        """
        """
        self.pool = Pool(self.worker_count, initializer=remote_host._init,
                        initargs=(self.queue,))

        self.listener = logger.Logger(target=logger.listener,
                                      args=(self.queue,
                                            self.name,
                                            self.log_file,
                                            desc))
        self.listener.start()
        res = self.pool.map_async(remote_host.process, self.conf)
        results = res.get(timeout)

        self.cleanup()
        return results

    def cleanup(self, terminate=False):
        if terminate:
            self.pool.terminate()
        else:
            self.pool.close()
        self.pool.join()
        self.queue.put_nowait(None)
        self.queue.close()
        self.listener.join()
