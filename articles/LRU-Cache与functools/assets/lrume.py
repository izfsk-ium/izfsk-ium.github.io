from pprint import pprint
from collections import deque

PREV, NEXT, VALUE = 0, 1, 2


class CircularDoublyLinkedList:
    def __init__(self) -> None:
        self.length = 0
        self.root = []  # circular doubly linked list
        self.root[:] = [self.root, self.root, None]  # PREV, NEXT, VALUE

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
        keyReturn = nodeToDelete[VALUE]
        tmp = self.root
        tmp[VALUE] = nodeToDelete[VALUE]
        self.root = tmp[NEXT]
        oldValue = nodeToDelete[VALUE]
        self.root[VALUE] = None
        self.length -= 1
        return keyReturn


class LRU_Cache2:
    def __init__(self, size) -> None:
        self.capacity = size
        self.item_list = deque()
        self.item_store = {}

    def getItem(self,key):
        target = self.item_store.get(key)
        if target is None:
            return None
        

class LRU_Cache:
    def __init__(self, size) -> None:
        self.capacity = size
        self.item_list = CircularDoublyLinkedList()  # Key queue
        self.item_store = {}  # real store

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


lRUCache = LRU_Cache(2)
lRUCache.setItem(1, 1)
# cache is {1=1}
lRUCache.setItem(2, 2)
# cache is {1=1, 2=2}
print(lRUCache.getItem(1))  # return 1
lRUCache.setItem(3, 3)
# LRU key was 2, evicts key 2, cache is {1=1, 3=3}
print(lRUCache.getItem(2))  # returns 0 (not found)
lRUCache.setItem(4, 4)
# LRU key was 1, evicts key 1, cache is {4=4, 3=3}
print(lRUCache.getItem(1))  # return 0 (not found)
print(lRUCache.getItem(3))  # return 3
print(lRUCache.getItem(4))  # return 4
