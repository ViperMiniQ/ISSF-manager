import time
import logging
from datetime import datetime
#from logging.handlers import SocketHandler

logger = logging.getLogger(__name__)
#socket_handler = SocketHandler('127.0.0.1', 19996)  # default listening address
#logger.addHandler(socket_handler)

def benchmark(function):  # change the name
    def __timing(*args, **kwargs):
        st = time.perf_counter()
        r = function(*args, **kwargs)
        logger.info(f"{function.__qualname__} - {datetime.now().strftime('%H:%M:%S')} - execution: {time.perf_counter() - st} seconds")
        return r

    return __timing
