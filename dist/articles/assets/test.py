def rstrip(iterable, pred):
    cache = []
    for x in iterable:
        if pred(x):
            cache.append(x)
        else:
            yield from cache
            cache.clear()
            yield x


print(list(rstrip([1, 2, None, 2, None], lambda x: x == None)))
