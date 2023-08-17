#include <gtk/gtk.h>

static void handle_activate(GApplication *app, gpointer *data) {
  g_printerr("Error: No file provided.");
}

static void handle_open(GApplication *app, gpointer *files, gint file_amount,
                        gchar *hint, gpointer *user_data) {
  GtkWidget *win;
  GtkWidget *scr;
  GtkWidget *tv;
  GtkTextBuffer *tb;
  char *contents;
  gsize length;
  char *filename;
  GError *err = NULL;

  win = gtk_application_window_new(GTK_APPLICATION(app));
  gtk_window_set_default_size(GTK_WINDOW(win), 400, 300);

  scr = gtk_scrolled_window_new();
  gtk_window_set_child(GTK_WINDOW(win), scr);

  tv = gtk_text_view_new();
  tb = gtk_text_view_get_buffer(GTK_TEXT_VIEW(tv));
  gtk_text_view_set_wrap_mode(GTK_TEXT_VIEW(tv), GTK_WRAP_WORD_CHAR);
  gtk_text_view_set_editable(GTK_TEXT_VIEW(tv), FALSE);
  gtk_scrolled_window_set_child(GTK_SCROLLED_WINDOW(scr), tv);

  if (g_file_load_contents(files[0], NULL, &contents, &length, NULL, &err)) {
    gtk_text_buffer_set_text(tb, contents, length);
    g_free(contents);
    if ((filename = g_file_get_basename(files[0])) != NULL) {
      gtk_window_set_title(GTK_WINDOW(win), filename);
      g_free(filename);
    }
    gtk_window_present(GTK_WINDOW(win));
  } else {
    g_printerr("%s.\n", err->message);
    g_error_free(err);
    gtk_window_destroy(GTK_WINDOW(win));
  }
}

int main(int argc, char **argv) {
  GtkApplication *application;

  application = gtk_application_new("org.izfsk.me", G_APPLICATION_HANDLES_OPEN);

  g_signal_connect(application, "activate", G_CALLBACK(handle_activate), NULL);
  g_signal_connect(application, "open", G_CALLBACK(handle_open), NULL);
  return g_application_run(G_APPLICATION(application), argc, argv);
}