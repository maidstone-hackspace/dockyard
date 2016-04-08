from gi.repository import Gtk as gtk
from libs.docker_helper import get_container_logs, get_container_info
from pprint import pprint
from gi.repository import GObject
import datetime


class LogWindow:
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file("glade/logs.glade")
        self.window = self.builder.get_object("window1")
        
        self.text_area = self.builder.get_object("textview1")
        self.lastChecked = 0
        self.timeoutActive = False

        self.window.connect('delete-event', self.hide_window)

    def show_logs(self, container_id):
        self.container_id = container_id
        self.container = get_container_info(container_id)
        #~ self.window = self.builder.get_object("window1")
        self.window.show_all()
        pprint(self.container)
        headerbar = self.builder.get_object("headerbar1")
        # headerbar.set_title(self.container['Name'][1:])
        # headerbar.set_subtitle(self.container['Config']['Image'])
        #~ self.set_text()
        self.timeoutActive = True
        GObject.timeout_add(1000, self.set_text)

    def hide_window(self, widget, *data):
        self.timeoutActive = False
        self.window.hide() 
        return True

    def set_text(self):
        if self.timeoutActive is False:
            return False
        #~ for line in get_container_logs(self.container_id, self.lastChecked).split("\n"):
            #~ date = datetime.datetime(line[0:30])
            #~ print date
        
        log_data = get_container_logs(self.container_id, self.lastChecked)
        self.lastChecked = datetime.datetime.now()

        last_timestamp = None
        for line in log_data.split("\n"):
            timestamp = line[0:line.find(' ')]
            print '-----'
            print timestamp
            last_timestamp = timestamp
        print(log_data)
        text_buffer = self.text_area.get_buffer()
        end_iter = text_buffer.get_end_iter()
        text_buffer.insert(end_iter, log_data)
        #~ buffer.insert_at_cursor(get_container_logs(self.container_id, self.lastChecked), -1)
        #buffer.set_text(get_container_logs(self.container_id, self.lastChecked))
        if timestamp:
            self.lastChecked = timestamp
        return True
        
