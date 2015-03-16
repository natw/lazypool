import threading
from Queue import Queue


ONE_YEAR = 365 * 24 * 60 * 60

THREAD_DONE = object()


class LazyThreadPoolExecutor(object):
    def __init__(self, num_workers=1):
        self.num_workers = num_workers
        self.result_queue = Queue()
        # is "reverse semaphore" a thing?
        self.thread_sem = threading.Semaphore(num_workers)

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
            with self.thread_sem:
                for thing in self.iterable:
                    self.result_queue.put(predicate(thing))
            self.result_queue.put(THREAD_DONE)
        return _w

    def _result_iterator(self):
        while 1:
            # Queue.get is not interruptable w/ ^C unless you specify a
            # timeout.
            # Hopefully one year is long enough...
            # See http://bugs.python.org/issue1360
            result = self.result_queue.get(True, ONE_YEAR)
            if result is not THREAD_DONE:
                yield result
            else:
                # if all threads have exited
                if self.thread_sem._Semaphore__value == self.num_workers:
                    break
                else:
                    continue



class ThreadSafeIterator(object):
    def __init__(self, it):
        self._it = iter(it)
        self.lock = threading.Lock()

    def __iter__(self):
        return self

    def next(self):
        with self.lock:
            return self._it.next()
