import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def benchmark(function):
    def __timing(*args, **kwargs):
        st = time.perf_counter()
        r = function(*args, **kwargs)
        logger.info(f"{function.__qualname__} - {datetime.now().strftime('%H:%M:%S')} - execution: {time.perf_counter() - st} seconds")
        return r

    return __timing
