---
uuid: "bce81e33-c008-4b15-8059-b5052cf00897"
title: "使用 glib 中的数据结构"
english: "Use-data-structures-in-glib"
date: 2023-09-05
category: "备忘"
outdated: false
draft: false
ref: 
  - name: "Manage C data using the GLib collections"
    url: "https://developer.ibm.com/tutorials/l-glib/"
  - name: "Hash Functions"
    url: "http://www.cse.yorku.ca/~oz/hash.html"
  - name: "GLib – 2.0"
    url: "https://docs.gtk.org/glib/index.html"
---

程序有两大构成要素，数据结构和算法，而在这两大要素中，因为数据结构是实现算法的基础，所以对各种常见数据结构的实现，在这两者中，优先性是第一位的。如果能在实现数据结构的过程中，开发出高可复用的类库，也能使开发者无比愉快，而在现实生活中，存在着对于这种类库的开发精益求精的项目，我们通常把这种类库称为标准库。对于 C 语言，这种类库不少，而 glib 是尤其突出常用的一种。

对于使用 `glib` 的程序，使用 `pkg-config` 编译：

```bash
cc -Wall `pkg-config --cflags glib-2.0` demo.c `pkg-config --libs glib-2.0`
```

## 单链表

glib 中最基础的数据结构是单向链表 `GSList`，对于单向链表，只能够从一个方向遍历。每次向其中添加一个新的项目，就创建一个新的 `GSList struct` 保存数据项和指向下一个内容的指针。以下是基本举例：

```c
#include <glib.h>
#include <stdio.h>

int main(int argc, char **argv) {
  /* 创建一个新的链表 */
  GSList *list = NULL;

  /* 添加新的项目， 注意将新的节点赋值给原来的*/
  list = g_slist_append(list, "Hello!");
  list = g_slist_append(list, "world");
  list = g_slist_append(list, "second");
  list = g_slist_append(list, "second");

  /* prepend 比 append 快速， 后者需要遍历整个链表 */
  list = g_slist_prepend(list, "apple");
  list = g_slist_prepend(list, "pie");

  /* 获取长度 */
  printf("Length of list : %d.\n", g_slist_length(list));

  /* 删除项目 */
  list = g_slist_remove(list, "apple");
  list = g_slist_remove_all(list, "second");
  printf("After remove, length of list : %d.\n", g_slist_length(list));

  /* 获取最后一个，第 n 个项目 */
  GSList *last_element = g_slist_last(list);
  GSList *second_element = g_slist_nth(list, 1);
  gpointer third_element = g_slist_nth_data(list, 2);
  printf("Last element : %s\n", last_element->data);
  printf("Second element : %s\n", second_element->data);
  printf("Third element : %s\n", third_element);

  g_slist_free(list);
  return 0;
}
```

`GSList` 对于用户自定义的类型也可以使用。

```c
#include <assert.h>
#include <glib.h>

typedef struct {
  unsigned int id;
  gboolean is_male;
  char *name;
} Person;

int main(int argc, char **argv) {
  GSList *list = NULL;

  /* 使用 malloc 进行内存管理 */
  Person *person_1 = (Person *)malloc(sizeof(Person));
  assert(person_1 != NULL);
  person_1->id = 0;
  person_1->is_male = TRUE;
  person_1->name = "John";
  list = g_slist_append(list, person_1);

  /* 使用 g_new 进行内存管理 */
  Person *person_2 = g_new(Person, 1);
  assert(person_2 != NULL);
  person_2->id = 1;
  person_2->is_male = FALSE;
  person_2->name = "Alice";
  list = g_slist_append(list, person_2);

  assert(g_slist_length(list) == 2);
  assert(((Person *)(g_slist_nth_data(list, 1)))->is_male == FALSE);
  assert(((Person *)(g_slist_nth_data(list, 1)))->id == 1);

  /* 内存释放 */
  free(person_1);
  g_free(person_2);
  g_slist_free(list);
  return 0;
}
```

要遍历整个链表，有两个方法：使用 `for` 循环，或者使用回调函数。

```c
#include <assert.h>
#include <glib.h>
#include <stdio.h>

inline static void callback(gpointer item, gpointer addition_data) {
  printf("%s %d\n", addition_data, item);
}

int main(int argc, char **argv) {
  GSList *list_1 = NULL;
  GSList *list_2 = NULL;
  for (int i = 0; i < 5; i++) {
    list_1 = g_slist_append(list_1, GINT_TO_POINTER(i));
    list_2 = g_slist_prepend(list_2, GINT_TO_POINTER(-i));
  }

  /* 使用 for 迭代 */
  for (GSList *ptr = list_1; ptr; ptr = ptr->next) {
    printf("list_1 : %d\n", ptr->data);
  }

  /* 使用回调 */
  g_slist_foreach(list_2, (GFunc)callback, "list_2 :");
}
```

`GList` 也提供列表合并，排序，倒序，寻找等常见功能（以上面的 `list_1` 和 `list_2` 为例）：

```c
inline static gint comper(gconstpointer item1, gconstpointer item2) {
  return item1 >= item2;
}

inline static gint finder(gconstpointer item) { return item == 1; }

...
  /* 列表合并 */
  GSList *concated = g_slist_concat(list_1, list_2);
  assert(g_slist_length(concated) == 10);

  /* 列表翻转 */
  GSList *reversed = g_slist_reverse(list_1);
  assert(g_slist_nth(list_1, 0)->data == g_slist_last(reversed)->data);

  /* 排序 */
  GSList *sorted = g_slist_sort(list_1, (GCompareFunc)comper);

  /* 寻找 */
  GSList *result = g_slist_find(concated, GINT_TO_POINTER(0));
  assert(result != NULL);
  result = g_slist_find_custom(concated, NULL, (GCompareFunc)(finder));
  assert(result != NULL);
  result = g_slist_find(concated, GINT_TO_POINTER(114514));
  assert(result == NULL);
...
```

## 双向链表

双向链表和单向链表类似，但是保存一个额外的指针指向上一个节点，因此可以实现双向查找使用。glib 中实现的双向链表名为 `GList`，大多数 `GSList` 可以使用的 API `GList` 都有类似的 API。以下是 `GList` 受益于前项指针所特有的操作：

```c
#include <glib.h>
#include <stdio.h>

int main(int argc, char **argv) {
  GList *list = NULL;
  for (int i = 0; i < 100; i++) {
    list = g_list_append(list, GINT_TO_POINTER(i));
  }

  GList *last = g_list_last(list);
  GList *first = g_list_first(list);
  GList *last_prev = g_list_previous(last);
  GList *last_prev_prev = g_list_nth_prev(last, 2);

  g_assert(last->data == GINT_TO_POINTER(99));
  g_assert(first->data == GINT_TO_POINTER(0));
  g_assert(last_prev->data == GINT_TO_POINTER(98));
  g_assert(last_prev_prev->data == GINT_TO_POINTER(97));
  g_list_free(list);
}
```

要寻找某个元素的位置，使用 `g_list_index` 和 `g_list_position`:

```c
gint index = g_list_index(list, GINT_TO_POINTER(25));
gint index_2 = g_list_position(list, g_list_last(list));
```

## 散列表

散列表使用散列函数来定位键，因此能快速执行操作。散列函数接收一个键，并为该键计算一个唯一值，称为散列。在 glib 中的散列表是 `GHashTable`。

创建散列表的函数是

```c
GHashTable* g_hash_table_new(GHashFunc hash_func, GEqualFunc key_equal_func);
```

要使用 `GHashTable`，需要提供一个 `GHashFunc` 和 `GEqualFunc`。两者的定义分别是

`typedef guint (*GHashFunc) (gconstpointer key);`

`typedef gboolean (*GEqualFunc)(gconstpointer a, gconstpointer b);`

前者对每个元素生成唯一的 Hash，后者比较两者的值。对于简单的 `String - String` 散列表，可以使用预定义的函数：

```c
#include <glib.h>

int main(int argc, char **argv) {
  /* g_str_hash 函数实现 "djb "哈希算法 */
  GHashTable *hash = g_hash_table_new(g_str_hash, g_str_equal);
  g_hash_table_insert(hash, "Virginia", "Richmond");
  g_hash_table_insert(hash, "Texas", "Austin");
  g_hash_table_insert(hash, "Ohio", "Columbus");
  return 0;
}
```

除此以外， glib 还有对于其他常见类型的 hash 函数。**注意：Hash 函数是针对 key 的，而不是对 value 的。**

![其他常见类型的 hash 函数](./assets/avilable_hashs.png)

对于哈希表的增删查改很容易完成：

```c
int main(int argc, char **argv) {
  GHashTable *hash = g_hash_table_new(g_str_hash, g_str_equal);

  /* 增 */
  g_hash_table_insert(hash, "A", "Aa");
  g_hash_table_insert(hash, "B", "Bb");
  g_hash_table_insert(hash, "C", "Cc");
  printf("There are %d keys in the hash\n", g_hash_table_size(hash));

  /* 删 */
  gboolean found = g_hash_table_remove(hash, "C");

  /* 查 */
  printf(g_hash_table_lookup(hash, "B"));

  /* 改 */
  g_hash_table_replace(hash, "A", "AAA");

  g_hash_table_destroy(hash);
  return 0;
}
```

Key-Value 遍历和查找：

```c
#include <glib.h>
#include <stdio.h>

inline static void iterator(gpointer key, gpointer value,
                            gpointer addition_data) {
  printf(addition_data, key, value);
}

int main(int argc, char **argv) {
  GHashTable *hash = g_hash_table_new(g_str_hash, g_str_equal);

  g_hash_table_insert(hash, "A", "Aa");
  g_hash_table_insert(hash, "B", "Bb");
  g_hash_table_insert(hash, "C", "Cc");

  g_hash_table_foreach(hash, (GHFunc)iterator, "%s -> %s\n");

  g_hash_table_destroy(hash);
  return 0;
}
```

除了 `g_hash_table_new` 以外，还有一个 `g_hash_table_new_full`，其签名如下：

```c
GHashTable *g_hash_table_new_full(GHashFunc hash_func,
                                  GEqualFunc key_equal_func,
                                  GDestroyNotify key_destroy_func,
                                  GDestroyNotify value_destroy_func);
```

其中 `key_destroy_func` 和 `value_destroy_func` 分别在 key 和 value 摧毁时调用。

```c
#include <glib.h>
#include <stdio.h>

void key_destroyed(gpointer data) { printf("key %s destroyed.\n", data); }

void value_destroyed(gpointer data) { printf("value %s destoryed\n", data); }

int main(int argc, char **argv) {
  GHashTable *hash = g_hash_table_new_full(g_str_hash, g_str_equal,
                                           (GDestroyNotify)key_destroyed,
                                           (GDestroyNotify)value_destroyed);
  g_hash_table_insert(hash, "A", "AA");
  g_hash_table_insert(hash, "B", "BB");

  g_hash_table_destroy(hash);
  return 0;
}
```

运行后将会显示：

```java
key B destroyed.
value BB destoryed
key A destroyed.
value AA destoryed
```

## 数组

除了链表，glib 还提供了另外一种顺序容器 `GArray` 来容纳指定类型的数据。相比于链表，`GArray` 拥有更快的访问速度。`GArray` 的初始化函数为:

`GArray *g_array_new(gboolean zero_terminated, gboolean clear_, guint element_size)`

其中，第一个参数是整个数组的内容是否为 '0' 结尾，第二个参数是每个元素是否初始化为 '0'。

```c
#include <glib.h>
#include <stdio.h>

#define PRINT_ARRAY_CONTENTS                                                   \
  for (int i = 0; i < array->len; i++) {                                       \
    printf(" [%d] : %s\n", i, g_array_index(array, char *, i));                \
  }

int main(int argc, char **argv) {
  GArray *array = NULL;
  array = g_array_new(FALSE, FALSE, sizeof(char *));

  /* 增加内容 */
  char *first = "hello", *second = "there", *third = "world", *forth = "forth";
  g_array_append_val(array, first);
  g_array_append_val(array, second);
  g_array_append_val(array, third);
  g_array_append_vals(array, argv, argc);
  g_array_prepend_val(array, first);
  g_array_prepend_vals(array, argv, argc);
  g_array_insert_val(array, 3, forth);

  /* 获取内容 */
  printf("Array size : %d\n", array->len);
  PRINT_ARRAY_CONTENTS;

  /* 删除内容 */
  g_array_remove_index(array, 0);
  g_array_remove_range(array, 1, 3);
  g_array_remove_index_fast(array, 0);
  printf("Array size after remove : %d\n", array->len);
  PRINT_ARRAY_CONTENTS;

  /* 排序 */
  printf("After sort:\n");
  g_array_sort(array, (GCompareFunc)(g_strcmp0));
  PRINT_ARRAY_CONTENTS;

  /* 释放 */
  g_array_free(array, FALSE);
}
```

除了基础的 `GArray`，glib 还提供了 `GPtrArray` 和 `GByteArray`:

```c
#include <glib.h>
#include <stdio.h>

int main(int argc, char **argv) {
  GPtrArray *array = g_ptr_array_new();

  char *buffer = (char *)malloc(1024);
  for (int i = 0; i < 16; i++) {
    sprintf(buffer, "%d,\n", i * i);
    g_ptr_array_add(array, g_strdup(buffer));
    memset(buffer, 0, 1024);
  }

  g_ptr_array_foreach(array, (GFunc)printf, NULL);
  g_ptr_array_free(array, TRUE);
  free(buffer);
}
```

`GByteArray` 最适合用来完成对二进制数据的「读取-扩容」循环：

```c
#include <glib.h>
#include <stdio.h>

GByteArray *read_file_to_byte_array(const char *file_path) {
  GByteArray *byte_array = g_byte_array_new();

  FILE *file = fopen(file_path, "rb");

  char buffer[1024];
  size_t bytes_read;
  while ((bytes_read = fread(buffer, 1, sizeof(buffer), file)) > 0) {
    g_byte_array_append(byte_array, (const guint8 *)buffer, bytes_read);
  }

  fclose(file);

  return byte_array;
}

int main(int argc, char **argv) {
  GByteArray *byte_array = read_file_to_byte_array(argv[1]);

  printf("Length of file : %ld\n", byte_array->len);
}
```

## 树

glib 提供两种树：平衡二叉树 `GTree` 和 n 叉树 `GNode`。 前者适合于树的每一个节点都只有不超过两个子节点，其内容被有序的存放以便快速搜索和查询。

```c
#include <glib.h>
#include <stdio.h>

#define PRINT_TREE_INFO                               \
  printf("Tree height : %d\n", g_tree_height(t));     \
  printf("Tree nodes : %d\n", g_tree_nnodes(t));

gboolean iter_all(gpointer key, gpointer value, gpointer data) {
  printf("%s, %s\n", key, value);
  return FALSE;
}

int main(int argc, char **argv) {
  GTree *t = g_tree_new((GCompareFunc)g_ascii_strcasecmp);
  /* 增 */
  g_tree_insert(t, "111", "A");
  g_tree_insert(t, "222", "B");
  g_tree_insert(t, "333", "C");
  PRINT_TREE_INFO;

  /* 删 */
  g_tree_remove(t, "d");
  PRINT_TREE_INFO;

  /* 查 */
  printf("%s\n", g_tree_lookup(t, "a") ? "Found" : "Not found");
  printf("%s\n", g_tree_lookup(t, "111") ? "Found" : "Not found");

  /* 改 */
  g_tree_replace(t, "1", "Z");

  /* 遍历 */
  g_tree_foreach(t, (GTraverseFunc)iter_all, NULL);

  g_tree_destroy(t);
  return 0;
}
```

## 队列

glib 提供的队列实现是 `GQueue`，其实现是基于双向链表 `GList`，因此也支持除队列操作以外的操作。当然，正常情况下不应该进行诸如「在队列中间插入一个元素」这样的操作，如果要经常这样做，不如考虑一下直接使用其他更高效的数据结构。

```c
#include <glib.h>
#include <stdio.h>

int main(int argc, char **argv) {
  GQueue *queue = g_queue_new();

  /* 增 */
  for (int i = 0; i < 5; i++) {
    g_queue_push_tail(queue, GINT_TO_POINTER(i));
  }
  g_queue_push_head(queue, GINT_TO_POINTER(-1));

  /* 长度信息 */
  gboolean is_empty = g_queue_is_empty(queue);
  gboolean length = g_queue_get_length(queue);
  printf("Length of queue : %d\n", length);

  /* 获取元素 */
  while (!g_queue_is_empty(queue)) {
    int data = (int)g_queue_pop_tail(queue);
    printf(data != -1 ? "%d, " : "%d\n", data);
  }

  g_queue_free(queue);
  return 0;
}
```

除了这些基本操作以外，`GQueue` 也支持 `g_queue_foreach` 等操作。

## 其他工具

- Base64 编码/解码

  ```c
  #include <glib.h>
  #include <stdio.h>
  #include <string.h>

  int main(int argc, char **argv) {
    if (argc != 2) {
      fprintf(stderr, "Bad usage.\n");
      return 1;
    }
    gchar *encoded = g_base64_encode(argv[1], strlen(argv[1]));
    printf("Base64 encoded : %s\n", encoded);

    gsize outlen;
    gchar *decoded = g_base64_decode(encoded, &outlen);
    printf("Base64 decoded : %s\n", decoded);
    printf("Raw text length : %lu\n", outlen);

    g_free(encoded);
    g_free(decoded);
    return 0;
  }
  ```

- 哈希函数

```c
#include <glib.h>
#include <stdio.h>
#include <string.h>

#define TEXT argv[1]
#define TEXT_LEN strlen(argv[1])

int main(int argc, char **argv) {
  if (argc != 2) {
    fprintf(stderr, "Bad usage.\n");
    return 1;
  }
  gchar *sha256 =
      g_compute_checksum_for_string(G_CHECKSUM_SHA256, TEXT, TEXT_LEN);
  gchar *sha512 =
      g_compute_checksum_for_string(G_CHECKSUM_SHA512, TEXT, TEXT_LEN);

  printf("sha512 : %s\nsha256 : %s\n", sha512, sha256);
  return 0;
}
```
