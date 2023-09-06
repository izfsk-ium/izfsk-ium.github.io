#include <glib.h>
#include <stdio.h>

#define PRINT_TREE_INFO                                                        \
  printf("Tree height : %d\n", g_tree_height(t));                              \
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
