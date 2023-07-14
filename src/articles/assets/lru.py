from functools import lru_cache
import time


def timeit(f):
    def func(*args, **kwargs):
        time_start = time.perf_counter()
        result = f(*args, **kwargs)
        print(f"{f.__name__} used {time.perf_counter()-time_start:.5f} seconds.")
        return result
    return func


@lru_cache(2048)
def fact(x):
    return 1 if x < 1 else x * fact(x - 1)


@timeit
def testA():
    fact(384)

@timeit
def testB():
    fact(384)

testA()
testB()