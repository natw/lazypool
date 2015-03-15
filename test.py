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

def msgs():
    while 1:
        p("POPPING")
        yield redis.blpop("foo")

def work(num):
    p("WORKING in thread {0}".format(threading.current_thread()))
    p(num)

pool = LazyThreadPoolExecutor(4)
pool.map(work, msgs())

import time
time.sleep(10)
