import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

#load the main interface files here globally
interface = Gtk.Builder()
interface.add_from_file('glade/gdocker.glade')
