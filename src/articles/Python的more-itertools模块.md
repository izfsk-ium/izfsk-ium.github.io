---
uuid: "426704c4-a51f-470c-a9c9-f3e3ecc43bfc"
title: Python的more-itertools模块
date: 2022-12-08
category: 学习
---

# 前提

所谓程序就是“一定的环境中处理数据”，日常编码中总是会碰到“在一个序列的数据中过滤”和“对序列中的每一个项目操作”这样的需求，我们可以这样做：

```python
for i in raw:
    if i.attribute == True:
        targetA.append(i)
    else:
        targetB.append(i)
for (index, target) in enumerate(targetA):
    targetA = do_something(target)

```

也可以类似Javascript这样:

```javascript
[1,2,3].filter(i => i > 2).map(i => i ** i);

```

当然，Python虽然提供了`map()`，`filter()`函数，但是不能够和JS那样链式调用，不过本文介绍的是比`map()`，`filter()`更加强大的函数们。

## 迭代器

简单的来讲，所谓迭代器，就是一个懒加载的列表。有一个指针`__next__()`指向“目前的项目”，调用这个指针就会“消费掉”这个值。而使用`list()`就能把整个迭代器变成列表。

迭代器比列表更加节省内存，因为每一个值会在需要的时候才计算。但是同样的，如果你试图把一个无限的迭代器转list，那就会爆内存。

# itertools

`itertools`是python提供的标准库，包含了许多帮助函数。这些函数的教程网上已经汗牛充栋，这里只提几个：

## Accumulate : 迭代操作器

按照字面意思翻译，这个函数应该叫做“累加器”，最基础的使用方法也是累加：

```python
list(itertools.accumulate([1,2,3]))
#[1, 3, 6]
```

这个函数相当于：

```python
list(itertools.accumulate([1,2,3],lambda x,y:x+y))
```

可以看到这个函数的第二个参数是一个函数。你可以给任意一个“输入两个值输出一个值”的函数，然后一步一步得到它的结果。换成`operator.mul`就是阶乘（`1*2，2*6，6*4......`）；换成`max`就是带过程的取最大值。

## Groupby : 数据分类汇总

假如你有这样的数据：

```json
data = [
    {"type": 1, "data": "John"},
    {"type": 1, "data": "Mike"},
    {"type": 2, "data": "Jenny"},
    {"type": 2, "data": "Wang"},
    {"type": 3, "data": "August"},
]
```

你想拿到这样的结果：

```python
[
    {"type": 1, "items": ["John", "Mike"]},
    {"type": 2, "items": ["Jenny", "Wang"]},
    {"type": 3, "items": ["August"]},
]
```

就可以使用这串魔法：

```python
[{'type':i,'items':[i['data'] for i in list(j)]} for i,j in itertools.groupby(data, key=lambda x: x["type"])]
```

其实也不是那么魔法，最重要的就是这一串：

`groupby(data, key=lambda x: x["type"])`

同样的，groupby函数接收两个参数，一个是迭代器，一个是函数类型，用来指定分类的key。可以理解成SQL`SELECT something FROM table GROUP BY key`中的`key`。返回类型是一个二元元组，(这个key，包含这个类别的元素的迭代器)。接下来就可以使用`list()`来转换了，这也是`[i['data'] for i in list(j)]`的作用。

:::{.note .blue}
|     |
| --- |
| ℹ️ groupby 在使用之前**一定**要对数据排序好！ |
:::

还是看不懂？那就看这个版本吧：

```python
result = list()

def keyFunction(item):
    return item["type"]

for key, iterator_of_items in itertools.groupby(data, key=keyFunction):
    list_of_items_of_this_type = list(iterator_of_items)

    result.append(
        {"type": key, "items": [i["data"] for i in list_of_items_of_this_type]}
    )
```

## Product : 全排列

假如你有'ABCD'和'xy'，你想要得到`Ax Ay Bx By Cx Cy Dx Dy`的排列组合，那么你就可以使用

`product('ABCD', 'xy')`来得到。很简单。函数签名是这样的：`itertools.product(*iterables, repeat=1)`，也就是你可以给出任何数量的迭代器。

## Pairwise : 成双成对，藕断丝连

`pairwise()`的用法很简单：`pairwise('ABCDEFG') --> AB BC CD DE EF FG`

它的实现方式类似于：

```python
def pairwise(iterable):
    # s -> (s0, s1), (s1, s2), (s2, s3), ...
    a, b = tee(iterable, 2)     # 获取两个指针
    next(b, None)               # 一个指针前移
    return zip(a, b)            # 配对
```

# more_itertools

好，现在进入高阶魔法阶段。这里将会一边介绍用法，一边简单分析源码。准备好：）

## 一变多系列

输入一个迭代器，返回多个结果的类型。

### Grouper

`more_itertools.grouper(iterable, n, incomplete='fill', fillvalue=None)`

按照给定的长度把一个可迭代类型分组。得到一个迭代器，里面包含指定长度的元组。

```python
list(grouper('ABCDEF', 3)) # 得到 [('A', 'B', 'C'), ('D', 'E', 'F')]
```

不过并不是每一个迭代器都能正好是整除你的`n`，所以`incomplete`和`fillvalue`控制不同的表现。假如你的分组目标是"ABCDEFG"，n=3，那么：

```python
list(grouper('ABCDEFG', 3, incomplete='fill', fillvalue='x'))  
# [('A', 'B', 'C'), ('D', 'E', 'F'), ('G', 'x', 'x')]
list(grouper('ABCDEFG', 3, incomplete='ignore', fillvalue='x')) 
# [('A', 'B', 'C'), ('D', 'E', 'F')]
list(grouper('ABCDEFG', 3, incomplete='strict'))
# 抛出异常 UnequalIterablesError
```

这玩意的实现机制很简单：

首先，如果你要展开一个iter，可以在它前面使用`*`号。比如` print(*iter([1,2,3]))`就会打印出`1 2 3`。

首先判断`incomplete`，如果是`ignored`，就直接上zip，否则，如果是`fill`的话，就使用`zip_longest(*args, fillvalue=fillvalue)`，是`strict`就使用`_zip_equal(*args)`。但核心是一样的，以`ignored`模式为例：

```python
zip(*[iter(target_iterable)] * n)
```

注意到`[iter()]*n`会创造出一个包含`n`个迭代器的列表，**其中每一个迭代器的内存地址是一样的**，操作一个就是操作全体！那么：

```python
a,b,c=[iter("hello!")]*3
# a <str_iterator at 0x7fd3b529ecb0>
# b <str_iterator at 0x7fd3b529ecb0>
# c <str_iterator at 0x7fd3b529ecb0>
list(zip(a,b,c))
# [('h', 'e', 'l'), ('l', 'o', '!')]
```

在这里，zip函数第一次取得的并不是`h,h,h`，而是`h,e,l`，因为每一次取得，所有三个指针的位置都会向前移动一格。

### Partition

`partition(pred, iterable)`：返回两个可迭代元素作为元组，前一个不符合你的条件，后一个符合你的条件。可以用来把一个迭代器一分为二成两个部分，<del>不同意的请站到左边，同意的请站到右边</del>。它的使用就比较普遍了。还记得文章开头的那个例子吗？就可以用这个函数来处理，这里另外举例。

```python
data = [
    {"type": 1, "data": "John"},
    {"type": 1, "data": "Mike"},
    {"type": 2, "data": "Jenny"},
    {"type": 2, "data": "Wang"}
]

is_allowed = lambda x: x["type"] == 1

allowed, forbidden = partition(is_allowed, files)
```

### Divide

顾名思义，这个函数把一个可迭代序列分割成若干个子迭代器。

```python
data = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh"]

[list(l) for l in divide(3, data)]
#  [['first', 'second', 'third'], ['fourth', 'fifth'], ['sixth', 'seventh']]
```

函数签名是`divide(n, iterable)`。其实现为，首先，尝试对`iterable`进行一个下标操作，通过捕获异常来判断类型：

```python
try:
    iterable[:0]
except TypeError:
    seq = tuple(iterable)   # 相当于是到元组类型的转换，因为迭代器类型不能取下标
else:
    seq = iterable          # 原来的输入是可以取下标的类型，例如普通列表
```

接着，使用`q, r = divmod(len(seq), n)`来获取商q和余数r。`divmod`是一个Python的内置函数，用来同时获得商和余数的元组。然后按照步长`n`结合q,r截取原来的列表构建结果列表：

```python
ret, stop = [], 0
for i in range(1, n + 1):
    start = stop
    if i <= r:
        stop += q + 1
    else:
        stop += q
    ret.append(iter(seq[start:stop]))
return ret
```

可以看到总是能够保证得到的结果会是`n`个迭代器。

### Split_XXX 系列

对于字符串，可以使用`'hello!world!'.split('!')`这样的方法把字符串分割成列表，那自然我们也希望能够对一个可迭代元素这样操作。`split_at()`函数接收的不是一个字符串而是一个函数，如果序列内的元素返回真，就在这里分割。其函数签名如下：`split_at(iterable, pred, maxsplit=-1, keep_separator=False)`。其中，`pred`是判断函数，`maxsplit`是最多分割次数，`keep_separator`决定是否保留真元素。

```python
[''.join(i) for i in more_itertools.split_at('hello!world',lambda x:x=='!',keep_separator=True)]
# ['hello', '!', 'world']
```

库里面还提供了其他几个函数，举例说明。约定`raw='aaaAaaaAaaaAaa'`，则：

| 函数      | 描述 | 示例 | 结果 |
| ----------- | ----------- | ----------- | ----------- |
| `split_at(iterable, pred, maxsplit=-1, keep_separator=False)`| 按照指定条件分割序列|`list(more_itertools.split_at(raw,lambda x:x=='A'))`|`[['a', 'a', 'a'], ['a', 'a', 'a'], ['a', 'a', 'a'], ['a', 'a']]`|
| `split_before(iterable, pred, maxsplit=-1)`|在返回真的元素之前分割，保留真元素|`list(more_itertools.split_before(raw,lambda x:x=='A'))`|`[['a', 'a', 'a'], ['A', 'a', 'a', 'a'], ['A', 'a', 'a', 'a'], ['A', 'a', 'a']]`|
|`split_after(iterable, pred, maxsplit=-1)`|在返回真的元素之后分割，保留真元素|`list(more_itertools.split_after(raw,lambda x:x=='A'))`|`[['a', 'a', 'a', 'A'], ['a', 'a', 'a', 'A'], ['a', 'a', 'a', 'A'], ['a', 'a']]`|

整个`split_xxx`系列都有类似的实现。首先判断`maxsplit`，为0就直接`yield list(iterator)`。再遍历原来序列的每一个元素，判断并按照要求`yield`即可：

```python
if maxsplit == 0:
    yield list(iterable)
    return

buf, it = [], iter(iterable)    # buf 是每一次返回的结果
for item in it:
    if pred(item):
        yield buf
        # 其他判断，略
        buf = []
        maxsplit -= 1
    else:
        buf.append(item)
yield buf                   # 返回结果，yield返回的依旧是一个生成器
```

注意这个函数返回的依旧是一个**generator object**，所以最后使用yield关键字。假如使用`split_at('00100',lambda x:x=='1')`的话，首先会`append`两次，把前面两个0放到结果中去，然后遇到1，直接把buf yield出去，下一次再进入时，buf再次被置零为空列表(第一个yield下面一行)再继续操作。最后遍历全部完成，再把剩下的返回。buf就是保存每一次结果的列表。其他split系列的函数实现类似，略有不同。

有两个函数与众不同，一个是`split_when`，这个函数接收的条件判断函数需要两个参数，返回真时则在这两个元素之间分割。例如，对输入`[1, 2, 3, 3, 2, 5, 2, 4, 2]`，判断函数拿到的就是`(1,2),(2,3),(3,3)......`这样的一组元素。实现上就需要用到双重指针了，一个指向目前项目，一个指向未来(next)项目。

```python
list(split_when([1, 2, 3, 3, 2, 5, 2, 4, 2], lambda x, y: x > y))
# [[1, 2, 3, 3], [2, 5], [2, 4], [2]]
```

另外一个是`split_into(iterable, sizes)`函数，很简单，就是按照sizes指定的大小列表分割：

```python
list(split_into([1,2,3,4,5,6], [1,2,3]))
# [[1], [2, 3], [4, 5, 6]]
```

实现起来相当简单，遍历sizes切分即可，基本上就相当于`[list(itertools.islice(iterator,i)) for i in sizes]`(所以返回的依旧是迭代器)。

## 多变一系列

### Flatten

打平，也就是把`[[1,2,3],[4,5]]`变成`[1,2,3,4,5]`这样的。可以想到把每一个每个子列表链接起来即可：

```python
list(itertools.chain.from_iterable([[1,2,3],[4,5]]))
```

然而，如果输入是多层嵌套的就会失败，假如输入`[[1,2,3],[4,5,[6,7]]]`，结果是`[1, 2, 3, 4, 5, [6, 7]]`。这种时候需要使用`collapse`。

### Collapse

用法不多说了，很简单。把一个多层嵌套的列表“打平”是常见的操作，一个常见的思路是使用递归：

```python
def flat(raw, result=[]):
    for i in raw:
        if type(i) == list:
            flat(i, result)
        else:
            result.append(i)
    return result
```

如果把它改写成生成器的写法就变成了：

```python
def flat(raw, result=[]):
    for i in raw:
        if type(i) == list:
            yield from flat(i, result)
        else:
            yield i
    yield from result
```

把for循环写到里面去，就变成：

```python
def flat(raw, result=[]):
    if type(raw) == list:
        for i in raw:
            yield from flat(i, result)
    else:
        yield raw
        return
```

这其实就是库的实现方式。不过它把内部循环单独实现了一下，限制了递归级数，并且加上了对bytes,str和用户定义的“不处理类型”的处理：

```python
def walk(node, level):
    if (((levels is not None) and (level > levels)) 
        or isinstance(node, (str, bytes)) 
        or ((base_type is not None) and isinstance(node, base_type))):
            yield node
            return
    try:
        tree = iter(node)
    except TypeError:
        yield node
        return
    else:
        for child in tree:
            yield from walk(child, level + 1)

yield from walk(iterable, 0)
```

它的函数签名是`collapse(iterable, base_type=None, levels=None)`，可以指定不处理的类型和递归层级。

### Unzip

`unzip`是标准函数`zip`的逆向过程。很容易理解，就是“先取每个迭代器的第一个组成第一个结果，再取每个迭代器的第二个组成第二个结果......”，实现方式类似于这样：

```python
raw = [("a", 1), ("b", 2), ("c", 3), ("d", 4)]

result = []
iterators = itertools.tee(raw, len(("a", 1)))   # 每一个原始类型元组的长度

for index, iterator in enumerate(iterators):
    result.append(list(map(lambda x: x[index], iterator)))
```

最终的结果是`[['a', 'b', 'c', 'd'], [1, 2, 3, 4]]`。库的实现是嵌套函数，并且返回的是一个`tuple`类型。但是请注意，如果输入类型不是严格匹配，参差不一的话会抛出`StopIteration`，其中的<del>间谍</del>`spy`的作用是拿到第一个元素和整个迭代器的副本并不去调用__next__()：

```python
head, iterable = spy(iter(iterable))
if not head:
    return ()
head = head[0]
iterables = tee(iterable, len(head))

def itemgetter(i):
    def getter(obj):
        try:
            return obj[i]
        except IndexError:
            raise StopIteration
    return getter

return tuple(map(itemgetter(i), it) for i, it in enumerate(iterables))
```

## 挨个操作系列

### Map_except

很简单的函数，如果你有一个参差不一的列表想要`map`但不希望因为里面有一堆不想要的数据类型导致抛出异常就使用它。此函数会简单的忽略出现的异常：

```python
def map_except(function, iterable, *exceptions):
    for item in iterable:
        try:
            yield function(item)
        except exceptions:
            pass
```

可以接收多个exception类型作为`exceptions`的参数，除此以外的不会被捕捉。当然，可以给一个`Exception`基类捕获一切异常。其实我来设计的话我会给它加一个默认值：

```python
def map_except(function, iterable, default, *exceptions):
    for item in iterable:
        try:
            yield function(item)
        except exceptions:
            yield default
```

### Map_reduce

组合拳，略复杂，看例子：

```python
data = [
    {"type": 1, "data": "John"},
    {"type": 1, "data": "Mike"},
    {"type": 2, "data": "Jenny"},
    {"type": 2, "data": "Wang"},
    {"type": 3, "data": "August"},
]

import more_itertools

result = more_itertools.map_reduce(
    data,
    lambda item: str(item["type"]), # 分类函数
    lambda data: 1, # 转换函数
    sum # 规约函数
)

# 得到 defaultdict(None, {'1': 2, '2': 2, '3': 1})
```

### Numeric_range

假设你要遍历1到10，你可以使用`range(1, 11)`，自然你也希望有一种方法可以遍历日期，分数，小数，乃至一切你直觉上觉得可以按照一定间隔遍历的东西，比如
`range(datetime(2022,11,11),datetime(2022,11,20))`这样，那么`numeric_range`就是你需要的：

```python
list(more_itertools.numeric_range(datetime(2022,11,11),datetime(2022,11,20)))
# 将会得到：
[datetime.datetime(2022, 11, 11, 0, 0),
 datetime.datetime(2022, 11, 12, 0, 0),
 datetime.datetime(2022, 11, 13, 0, 0),
 datetime.datetime(2022, 11, 14, 0, 0),
 datetime.datetime(2022, 11, 15, 0, 0),
 datetime.datetime(2022, 11, 16, 0, 0),
 datetime.datetime(2022, 11, 17, 0, 0),
 datetime.datetime(2022, 11, 18, 0, 0),
 datetime.datetime(2022, 11, 19, 0, 0)]
```

首先，`numberic_range`是一个继承了`abc.Sequence`和`abc.Hashable`的类，这也就意味着它并不是一个`iterator`。按照文档，继承了`Sequence`就要实现一些方法：

```python
class C(Sequence):                      # Direct inheritance
    def __init__(self): ...             # Extra method not required by the ABC
    def __getitem__(self, index):  ...  # Required abstract method
    def __len__(self):  ...             # Required abstract method
    def count(self, value): ...         # Optionally override a mixin method
```

与`range`函数相同，它的构造函数也接收一到三个参数，即起，末和间隔。无论给出的是多少个参数，在构造函数
中会生成`self._start`,`self._stop`,`self._step`代表起，末和间隔。为了自动推导出来，在构造函数中使用了一些技巧，也就是`type`函数。比如给出参数`4,5`，那么会使用这样的方法得出
第三个参数(自动指定间隔为1)：

```python
start,stop = (4,5)
step = type(stop - start)(1)
```

`__getitem__`可以处理int的key或者slice的key，按照不同的类型返回不同结果。如果是简单的获取指定位置的元素，只需要`self._start + i * self._step`即可。

同样的，使用`self._zero = type(self._step)(0)`就可以得到这个类型的0值。除此以外，构造函数还需要判断给出的起末是递增的还是递减的，这个判断使用`self._step > self._zero`来实现。最简示例如下：

```python
class numeric_range(abc.Sequence, abc.Hashable):
    def __init__(self, *args):
        self._start, self._stop, self._step = args
        # datetime(2020, 2, 10), datetime(2020, 2, 15), timedelta(days=2)
        self._zero = type(self._step)(0)
        # timedelta(0)
        self._growing = self._step > self._zero
        # True
        q, r = divmod(self._stop - self._start, step)
        self._len = int(q) + int(r != self._zero)
        # 3

    def __getitem__(self, key):
        return self._start + i * self._step

    def __hash__(self):
        return hash((self._start, self._get_by_index(-1), self._step))

    def __len__(self):
        return self._len

start = datetime.datetime(2020, 2, 10)
stop = datetime.datetime(2020, 2, 15)              
step = datetime.timedelta(days=2)   
x = numeric_range(start, stop, step)
```

## 过滤器系列

### Strip 系列

像字符串的`strip`函数一样，对一个序列进行操作，去除末尾元素。不过接收的是一个函数类型：

```python
iterable = (None, False, None, 1, 2, None, 3, False, None)

# [False, None, 1, 2, None, 3, False]
list(more_itertools.strip(iterable,lambda x:x == None))

# [False, None, 1, 2, None, 3, False, None]
list(more_itertools.lstrip(iterable,lambda x:x == None))

# [None, False, None, 1, 2, None, 3, False]
list(more_itertools.rstrip(iterable,lambda x:x == None))
```

`lstrip`的实现就是一个` dropwhile(pred, iterable)`，而`rstrip`使用一个列表来处理符合条件的元素：


```python
def rstrip(iterable, pred):
    cache = []
    for x in iterable:
        if pred(x):
            cache.append(x)
        else:
            yield from cache
            cache.clear()
            yield x
```

### Filter_except

和`map_except`类似，不过是一个过滤操作：

```python
data = ['1.5', '6', 'not-important', '11', '1.23E-7', 'remove-me', '25', 'trash']
list(map(float, filter_except(float, data, TypeError, ValueError)))
#  [1.5, 6.0, 11.0, 1.23e-07, 25.0]
```

# 参考

- [more_itertools文档](https://more-itertools.readthedocs.io/en/stable/_modules/more_itertools/more.html "Source code for more_itertools.more")
- [functools介绍文章](https://martinheinz.dev/blog/52 "Functools - The Power of Higher-Order Functions in Python")
- [itertools文档](https://docs.python.org/3/library/itertools.html#itertools-recipes "Itertools Recipes")


