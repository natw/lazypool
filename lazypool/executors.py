import threading

print_lock = threading.Lock()
def p(x):
    with print_lock:
        print x

class LazyThreadPoolExecutor(object):
    def __init__(self, num_workers=1):
        self.num_workers = num_workers

    def map(self, predicate, iterable):
        self.iterable = ThreadSafeIterator(iterable)
        for i in range(self.num_workers):
            t = threading.Thread(
                name="LazyChild #{0}".format(i),
                target=self._make_worker(predicate)
            )
            t.daemon = True
            t.start()

    def _make_worker(self, predicate):
        def _w():
            p("the worker: %s" % threading.current_thread())
            for thing in self.iterable:
                predicate(thing)
        return _w


class ThreadSafeIterator(object):
    def __init__(self, it):
        self._it = it
        self.lock = threading.Lock()

    def __iter__(self):
        return self

    def next(self):
        with self.lock:
            return self._it.next()
