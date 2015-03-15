import threading
from Queue import Queue

print_lock = threading.Lock()
def p(x):
    with print_lock:
        print x

ONE_YEAR = 365 * 24 * 60 * 60

class LazyThreadPoolExecutor(object):
    def __init__(self, num_workers=1):
        self.num_workers = num_workers
        self.result_queue = Queue()

    def map(self, predicate, iterable):
        self.iterable = ThreadSafeIterator(iterable)
        for i in range(self.num_workers):
            t = threading.Thread(
                name="LazyChild #{0}".format(i),
                target=self._make_worker(predicate)
            )
            t.daemon = True
            t.start()
        return self._result_iterator()

    def _make_worker(self, predicate):
        def _w():
            p("the worker: %s" % threading.current_thread())
            for thing in self.iterable:
                self.result_queue.put(predicate(thing))
        return _w

    def _result_iterator(self):
        while 1:
            # Queue.get is not interruptable w/ ^C unless you specify a
            # timeout.
            # Hopefully one year is long enough...
            # See http://bugs.python.org/issue1360
            yield self.result_queue.get(True, ONE_YEAR)


class ThreadSafeIterator(object):
    def __init__(self, it):
        self._it = it
        self.lock = threading.Lock()

    def __iter__(self):
        return self

    def next(self):
        with self.lock:
            return self._it.next()
