---
uuid: "809dd759-e6d9-4bb0-8e9b-31e48c7a9366"
title: LRU-Cache与functools
date: 2022-12-13
category: 算法
---

# 啥是 LRU Cache

LRU的全称是 Least recently used，也就是「最近最少使用」，这是一种用来管理缓存的机制。缓存的容量是有限的，不能无限制的放各种数据，通常，在缓存里面放容易命中的常用数据肯定比放冷门的数据好，LRU机制假设一个数据如果在最近一段时间没有被访问，那么它在未来被访问的可能性也比较小。由此，在缓存满了以后，就通过淘汰最近没有用过的数据项来更新。


# 实现思路

先陈述一下思路，目标是实现一个 `LRUCache` 类，可以参照 [leetcode](https://leetcode.com/problems/lru-cache/) 上的题目来做。

实现一个朴素的 lru cache 需要两个容器，一个双向链表 (item) 用来保存数据权重，一个哈希表 (key:item) 用来保存实际的数据，和链表相互配合。除此以外还需要一个缓存最大大小。保存实际数据的是一个类似于 pair 的结构 LRU_Item ，使用 `decltype` 来推导类型。

```c++
// 大小
const long capacity;
// 保存权重
list<LRU_Item<Key_T, Val_T>> items;
// 保存实际数据，真实数据是LRU_Item类型中的Val_T的类型
unordered_map<Key_T, decltype(items.begin())> items_map;
```

当访问一个数据项时，从哈希表中寻找目标，如果找不到，返回这个模板类型的默认值，否则就命中缓存项目，**之后，更新权重表**，将目标 key 提到列表的最前面即将该数据移至链表头部。当插入一个数据项目时，如果已经存在项目 key ，删除旧项目，之后作为最新的项目在链表的最前面插入，再检查缓存大小，将多余的项目排除。虽然使用一个定长的双向链表也能实现，但使用哈希表降低了操作的复杂度。

举例：假设有一个 Cache ，其容量为2，首先插入一条数据 `(k=1,v=1)` :

`{ (1:1) }`

接下来插入一条数据 `(k=2,v=2)` :

`[ (2:2) (1:1) ]`

接下来获取 `key=1` ，则返回结果后缓存内容变为：

`[ (1:1) (2:2) ]`

可以看到 `(1:1)` 被提到了最前面。如果在这时再次插入一个 `(k=3,v=3)` ，由于容量为2，最不常用的也就是处于列表最末尾的元素被移除，新的元素插入开头:

`[ (3:3) (1:1) ]`

## C++

以下是 C++ 实现的 LRU-Cache 类：

```c++
#include <unordered_map>
#include <list>

using namespace std;

template <typename KT, typename VT> struct LRU_Item {
    public:
        KT key; VT value;
        LRU_Item(KT key,VT value):key(key),value(value) { ; }
};

template <typename Key_T, typename Val_T> class LRU_Cache {
    public:
        LRU_Cache(int capacity):capacity(capacity) { ; }
        void putItem(const Key_T &key, const Val_T &value);
        const Val_T getItem(const Key_T &key);
    private:
        const long capacity;
        list<LRU_Item<Key_T, Val_T>> items;
        unordered_map<Key_T, decltype(items.begin())> items_map;
};

template <typename Key_T, typename Val_T>
void LRU_Cache<Key_T, Val_T>::putItem(const Key_T &key, const Val_T &value){
    auto iter = this->items_map.find(key);
    if (iter != this->items_map.end()){
        // delete exists item and insert in front of list
        this->items.erase(iter->second);
        this->items_map.erase(iter);
    }
    // insert element in front of the list
    auto element = LRU_Item<Key_T,Val_T>(key,value);
    this->items.push_front(element);
    // store it into map
    this->items_map.insert(make_pair(key, this->items.begin()));
    // check size and strip
    for (int i = this->items_map.size() - this->capacity ; i > 0; i--){
        auto iter = this->items.end();
        this->items_map.erase((--iter)->key);
        this->items.pop_back();
    }
}

template <typename T> struct I { T _; I():_() { ; } };

template <typename Key_T, typename Val_T>
const Val_T LRU_Cache<Key_T, Val_T>::getItem(const Key_T &key){
    auto iter = this->items_map.find(key);
    if (iter ==  this->items_map.end()){
        // not found, return default value
        return (new I<Val_T>())->_;
    }
    // update list, put iter to the first
    this->items.splice(this->items.begin(), this->items, iter->second);
    return iter->second->value;
}
```

测试用例（采取 leetcode 的测试代码）：

```c++
int main(int argc, char **argv){
    auto lRUCache = new LRU_Cache<int,int>(2);
    lRUCache->putItem(1, 1); // cache is {1=1}
    lRUCache->putItem(2, 2); // cache is {1=1, 2=2}
    cout << lRUCache->getItem(1) << endl;    // return 1
    lRUCache->putItem(3, 3); // LRU key was 2, evicts key 2, cache is {1=1, 3=3}
    cout << lRUCache->getItem(2) << endl;    // returns 0 (not found)
    lRUCache->putItem(4, 4); // LRU key was 1, evicts key 1, cache is {4=4, 3=3}
    cout << lRUCache->getItem(1) << endl;    // return 0 (not found)
    cout << lRUCache->getItem(3) << endl;    // return 3
    cout << lRUCache->getItem(4) << endl;    // return 4
}
```

请注意，这里的代码**并不一定是最佳的解答，效率和性能也不一定最好**，但求清晰。

## Python

### 双向链表的模拟

当然也可以采用 Python 实现。使用一个 list 和一个 dict 可以轻松的完成任务，但为了和设计一致，在这里使用 python 的列表来模拟循环双向链表(这也是 `Lib/functools.py` 的实现方式)。

**不得不吐槽，你必须把自己的思想扭曲到一定程度才能熟练而自然的在 python 里面模拟指针类型和循环双向链表**，以下是一个实现：

```python
PREV, NEXT, VALUE = 0, 1, 2

class CircularDoublyLinkedList:
    def __init__(self) -> None:
        self.length = 0
        self.root = [] 
        self.root[:] = [self.root, self.root, None] 
        # PREV, NEXT, VALUE

    def insert(self, value):
        newNode = [None, None, value]
        last = self.root[PREV]
        newNode[PREV] = last
        newNode[NEXT] = self.root
        last[NEXT] = self.root[PREV] = newNode
        self.length += 1

    def getNode(self, index):
        if index < 0 or index > self.length:
            raise IndexError()
        tmp = self.root[NEXT]
        for i in range(index):
            tmp = tmp[NEXT]
        return tmp

    def get(self, index):
        return self.getNode(index)[VALUE]

    def swapEnd(self, index):
        targetNode = self.getNode(index)
        prev, next, value = targetNode
        # delete node
        prev[NEXT] = next
        next[PREV] = prev
        # insert into the end of the list
        last = self.root[PREV]
        last[NEXT] = self.root[PREV] = targetNode
        targetNode[PREV] = last
        targetNode[NEXT] = self.root

    def search(self, value) -> int:
        tmp = self.root[NEXT]
        for i in range(self.length):
            if tmp[VALUE] == value:
                return i
            tmp = tmp[NEXT]
        return -1

    def stripLeft(self):
        nodeToDelete = self.getNode(self.length - 1)
        tmp = self.root
        tmp[VALUE] = nodeToDelete[VALUE]
        self.root = tmp[NEXT]
        oldValue = nodeToDelete[VALUE]
        self.root[VALUE] = None
        self.length -= 1
```

虽然在这里「模拟」出了双向链表，你以为的链表内容:

```python
[ [<pointer>, <pointer>, 1], [<pointer>, <pointer>, 2] ... [<pointer>, <pointer>, 999] ]
```

但其实是:

```python
[[[[<Recursion on list with id=140593175582080>,
    <Recursion on list with id=140593172979712>,
    0],
   <Recursion on list with id=140593173013888>,
   1],
  <Recursion on list with id=140593175582080>,
  2],
 [<Recursion on list with id=140593175582080>,
  [<Recursion on list with id=140593173014784>,
   [<Recursion on list with id=140593172979712>,
    <Recursion on list with id=140593175582080>,
    2],
   1],
  0],
 None]
```

这也就意味着，但凡是比较大的列表，就会 `RecursionError: maximum recursion depth exceeded while calling a Python object` 。

那么接下来使用这个脆弱的双向链表来实现一个脆弱的 LRU_Cache ，注意，和 C++ 实现不同，这里的 item_list 是**反过来存储**的，也就是最新的元素插入在右端，去除的是左端的内容:

```python
class LRU_Cache:
    def __init__(self, size) -> None:
        self.capacity = size
        self.item_list = CircularDoublyLinkedList()  # Key queue
        self.item_store = dict()  # real store

    def getItem(self, key):
        target = self.item_store.get(key)
        if target is None:
            return None
        self.item_list.swapEnd(self.item_list.search(key))
        return target

    def setItem(self, key, value):
        if self.getItem(key) != None:
            self.item_list.delete(self.item_list.searchKey(key))
            del self.item_store[key]
        self.item_store[key] = value
        self.item_list.insert(key)
        if self.capacity < self.item_list.length:
            keyD = self.item_list.get(0)
            self.item_list.stripLeft()
            del self.item_store[keyD]
```

这个实现可以通过测试,<del>但也只保证通过测试(</del>

### collections.deque

其实使用双向链表之类的目的在于能够快捷的处理「在初始插入」之类的操作，但这种操作在标准库 `collections` 中已经被 [`deque`](https://docs.python.org/3.3/library/collections.html#collections.deque) 提供了。`deque` 是一个内置类型，使用 C 实现，位于源码 `Modules/_collectionsmodule.c` ，库路径位于 `lib64/python/lib-dynload/_collections.so` 。它提供了 `appendLeft` , `popLeft` 这类操作。

对于 deque 来说，删除任意位置元素可以这样实现：

```python
def delete_nth(d, n):
    d.rotate(-n)
    d.popleft()
    d.rotate(n)
```

再将删除的元素重新排到末尾即可实现 `swapEnd` 。其他的操作和之前类似。

# functools

所谓装饰器，可以理解为「操作函数的函数」。实际上就是定义了一个函数，这个函数接收另外一个函数，作出一些修改，再返回这个函数。而「装饰器」是这个过程的语法糖。

## @lru_cache

`lru_cache` 的函数原型是 `@functools.lru_cache(maxsize=None, typed=False)`，使用 lru 缓存机制，可以设定最大缓存数量。真正的缓存实现位于 [`_lru_cache_wrapper`](https://github.com/python/cpython/blob/00e24cdca422f792b80016287562b6b3bccab239/Lib/functools.py#L478) 函数中。该函数使用列表模拟的双向循环链表+ dict 的方式存储缓存。

可以像这样来使用：

```python
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
```

结果：

```
testA used 0.00023 seconds.
testB used 0.00000 seconds.
```

可以看到 lru_cache 显著降低了时间。

# 参见

- [模板类返回类型默认值](https://stackoverflow.com/questions/5300602/template-return-type-with-default-value "Template Return Type with Default Value")
- [functools 源码](https://github.com/python/cpython/blob/00e24cdca422f792b80016287562b6b3bccab239/Lib/functools.py#L478) 