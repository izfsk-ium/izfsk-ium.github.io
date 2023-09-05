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

/*
key B destroyed.
value BB destoryed
key A destroyed.
value AA destoryed
*/