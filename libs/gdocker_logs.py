from gi.repository import Gtk as gtk
from libs.docker_helper import get_container_logs, get_container_info
from pprint import pprint
from gi.repository import GObject
import datetime


class LogWindow:
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file("glade/logs.glade")
        self.lastChecked = 0

    def show_logs(self, container_id):
        self.container_id = container_id
        self.container = get_container_info(container_id)
        self.window = self.builder.get_object("window1")
        self.window.show_all()
        pprint(self.container)
        headerbar = self.builder.get_object("headerbar1")
        # headerbar.set_title(self.container['Name'][1:])
        # headerbar.set_subtitle(self.container['Config']['Image'])
        self.set_text()

    def set_text(self):
        text_area = self.builder.get_object("textview1")
        buffer = text_area.get_buffer()
        buffer.insert_at_cursor(get_container_logs(self.container_id, self.lastChecked), -1)
        self.lastChecked = datetime.datetime.now().time()
        text_area.set_buffer(buffer)
        GObject.timeout_add(60, self.set_text)