from gi.repository import Gtk as gtk


class LogHandler:
    def onDeleteWindow(self, *args):
        gtk.main_quit(*args)

    def on_refresh_clicked(self, button):
        print("Hello World!")


class LogWindow:
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file("glade/logs.glade")
        self.builder.connect_signals(LogHandler())

    def show_logs(self, container):
        self.window = self.builder.get_object("window1")
        self.window.show_all()
        headerbar = self.builder.get_object("headerbar1")
        headerbar.set_title(container['Name'][1:])
        headerbar.set_subtitle(container['Image'])
        self.set_text(container)

    def set_text(self, container):
        text_area = self.builder.get_object("textview1")
        print dir(container)
        print dir(text_area)
        text_area.set_text(container)