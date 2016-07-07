import multiprocessing
from multiprocessing import Pool
import logging
import logging.handlers
import time
from datetime import datetime

def listener(queue, name, log_file):
    root = logging.getLogger(name)
    root.setLevel(logging.INFO)

    # write file header
    with open(log_file, 'w') as f:
        f.write('[\n')
        f.close

    # setup log file handler
    # TODO: add desc as a parameter
    desc = 'action'
    fileHandler = logging.FileHandler(log_file, mode='a')
    formatter = logging.Formatter(
        "\t{'timestamp': %(unixtime)s, 'message': '%(message)s', " +
        "desc: '{}', 'datetime': '%(isotime)s'}},".format(desc)
    )
    fileHandler.setFormatter(formatter)
    root.addHandler(fileHandler)

    while True:
        try:
            raw_record = queue.get()
            #print(raw_record)
            if raw_record is None:
                break
            logger = logging.getLogger(name)
            record = logger.makeRecord(raw_record.name,
                                       raw_record.levelno,
                                       raw_record.filename,
                                       raw_record.lineno,
                                       raw_record.message,
                                       raw_record.args,
                                       raw_record.exc_info,
                                       extra=get_times())
            fileHandler.handle(record)
        except Exception as ex:
            print(ex)
            print('Whoops! Problem:')

    # write file footer
    with open(log_file, 'a') as f:
        f.write(']')
        f.flush()
        f.close()


def get_times():
    tm = int(time.time())
    dt = datetime.utcfromtimestamp(tm).isoformat()
    times = {'unixtime': tm, 'isotime': dt}
    return times

class Logger(multiprocessing.Process):

    def __init__(self, *args, **kwargs):
        super(Logger, self).__init__(*args, **kwargs)

