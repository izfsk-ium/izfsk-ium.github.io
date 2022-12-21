#include <iostream>
#include <unordered_map>
#include <list>

#include <spdlog/spdlog-inl.h>

using namespace std;

template <typename KT, typename VT> struct LRU_Item {
    public:
        KT key; VT value;
        LRU_Item(KT key,VT value):key(key),value(value) { ; }
};

template <typename Key_T, typename Val_T> class LRU_Cache {
    public:
        LRU_Cache(int capacity):capacity(capacity) { ; }
        // Put item in cache
        void putItem(const Key_T &key, const Val_T &value);
        // Get item in cache
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

// wrapper for the default value
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

int main(int argc, char **argv){
    spdlog::info("Welcome to spdlog!");
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
