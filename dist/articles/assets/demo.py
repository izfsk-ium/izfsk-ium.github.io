def fib(stop: int):
    a, b = 1, 1
    yield a
    for i in range(stop):
        yield a
        c = a + b
        a = b
        b = c


def recur_fib(n):
    if n <= 1:
        return n
    else:
        return recur_fib(n - 1) + recur_fib(n - 2)


def coro_creator(raw, *args):
    coro = raw(*args)
    next(coro)
    return coro


i = coro_creator(fib, 16)
print(i.send(10))
