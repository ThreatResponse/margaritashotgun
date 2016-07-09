import multiprocessing
from multiprocessing import Pool
import logging
import logging.handlers
import time
from datetime import datetime

def listener(queue, name, log_file, desc):
    root = logging.getLogger(name)

    # write file header
    with open(log_file, 'w') as f:
        f.write('[\n')
        f.close

    # setup log file handler
    fileHandler = logging.FileHandler(log_file, mode='a')
    formatter = logging.Formatter(
        "\t{'timestamp': %(unixtime)s, 'message': '%(message)s', " +
        "desc: '{}', 'datetime': '%(isotime)s'}},".format(desc)
    )
    fileHandler.setFormatter(formatter)

    while True:
        try:
            raw_record = queue.get()
            if raw_record is None:
                break
            logger = logging.getLogger(raw_record.name)
            record = logger.makeRecord(raw_record.name,
                                       raw_record.levelno,
                                       raw_record.filename,
                                       raw_record.lineno,
                                       raw_record.message,
                                       raw_record.args,
                                       raw_record.exc_info,
                                       extra=get_times())
            fileHandler.handle(record)
        except KeyboardInterrupt:
            # Parent process to terminate
            pass
        except Exception as ex:
            print(ex)
            break

    cleanup(log_file)

def get_times():
    tm = int(time.time())
    dt = datetime.utcfromtimestamp(tm).isoformat()
    times = {'unixtime': tm, 'isotime': dt}
    return times

def cleanup(log_file):
    with open(log_file, 'a') as f:
        f.write(']')
        f.flush()
        f.close()


class Logger(multiprocessing.Process):

    def __init__(self, *args, **kwargs):
        super(Logger, self).__init__(*args, **kwargs)

