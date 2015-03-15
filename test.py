from redis import StrictRedis
from lazypool import LazyThreadPoolExecutor
from lazypool.executors import p
import threading

redis = StrictRedis()

redis.rpush("foo", 1)
redis.rpush("foo", 2)
redis.rpush("foo", 3)
redis.rpush("foo", 4)
redis.rpush("foo", 5)

def infinite():
    while 1:
        p("POPPING")
        yield redis.blpop("foo")

def finite():
    for i in range(10):
        yield i


def work(num):
    p("WORKING in thread {0}".format(threading.current_thread()))
    p(num)
    return "did work"

pool = LazyThreadPoolExecutor(4)
results = pool.map(work, finite())

for r in results:
    print "hi"
    print r

# import time
# time.sleep(10)

print "done"
