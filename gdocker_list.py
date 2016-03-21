#!/usr/bin/env python
# [SNIPPET_NAME: gtk3 listbox example]
# [SNIPPET_CATEGORIES: opengl]
# [SNIPPET_TAGS: touch, gtk3]
# [SNIPPET_DESCRIPTION: add rows to a listbox based on retrieved interface file]
# [SNIPPET_AUTHOR: Oliver Marks ]
# [SNIPPET_LICENSE: GPL]

import sys
import gi
#~ gi.require_version('Gtk', '3.0')
#~ gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify

from settings import APPINDICATOR_ID
from libs.docker_helper import get_containers, get_container, get_container_info, get_container_forwards, container_iface, container_proxy
from libs.listbox_rows import ListBoxSelect
from libs.container_images import image_browser
from libs.utils import return_browsers
from libs.core import interface

class AppWindow(object):
    """Tutorial 13 custom treeview list boxes"""
    count = 0
    retrieve_job = None

    def __init__(self, app):
        #~ super(AppWindow, self).__init__(*args, **kwargs)
        #~ Gtk.Application.__init__(self)
        # load in our glade interface
        interface = Gtk.Builder()
        interface.add_from_file('glade/gdocker.glade')

        self.image_browser = image_browser()

        # grab our widget using get_object this is the name of the widget from glade, window1 is the default name
        self.window = interface.get_object('root_window')
        self.window.set_application(app)
        self.window_prefs = interface.get_object('prefs_window')
        self.window_menu = interface.get_object('root_window_menu')
        self.window_menu_prefs = interface.get_object('root_window_prefs')

        # load our widgets from the glade file
        self.widgets = {}
        self.widgets['searchentry'] = interface.get_object('search_containers')
        self.widgets['searchentrycompletion'] = interface.get_object('search_container_completion')
        self.widgets['searchentry'].set_completion(self.widgets['searchentrycompletion'])

        self.widgets['open_registry'] = interface.get_object('btn_open_registry')
        self.widgets['open_registry'].connect('button_press_event', self.show_image_list)
        self.widgets['searchentry'].connect('changed', self.refresh_list)
        self.widgets['listbox'] = interface.get_object('listbox1')
        self.widgets['progress'] = interface.get_object('listProgress')
        self.widgets['refresh'] = interface.get_object('btnRefresh')
        self.widgets['message_dialog'] = interface.get_object('dialog_confirm')
        self.widgets['refresh'].connect('button_press_event', self.refresh_list)
        self.widgets['close'] = interface.get_object('btnClose')
        self.widgets['close'].connect('button_press_event', self.closeFetcher)

        # wrap the listbox so we can reuse the code, pass in the listbox widget to our wrapper class
        self.listbox = ListBoxSelect(self.widgets['listbox'], self.widgets['message_dialog'])

        # connect to events, in this instance just quit our application
        self.window.connect('delete_event', Gtk.main_quit)
        self.window.connect('destroy', lambda quit: Gtk.main_quit())

        container_proxy.connect_to_signal("state_change", self.refresh_list, dbus_interface="org.freedesktop.container")

        # show the window else there is nothing to see :)
        self.openFetcher()
        self.populate_prefs()
        self.refresh()

    def populate_prefs(self):
        self.prefs_select_browser = interface.get_object('cmb_prefs_select_browser')
        for browser, path in return_browsers():
            print browser
            self.prefs_select_browser.append_text(browser)
        self.prefs_select_browser.set_active(0)
        self.window_prefs.show_all()

    #~ def do_startup(self):
        #~ Gtk.Application.do_startup(self)
        
        #~ menu = Gio.Menu()
        #~ # append to the menu three options
        #~ menu.append("Prefs", "app.new")
        #~ menu.append("About", "app.about")
        #~ menu.append("Quit", "app.quit")
        #~ self.set_app_menu(menu)

        #~ self.set_menubar(self.window_menu_prefs)
        
        #~ self.set_menubar(self.window_menu)

    def openFetcher(self):
        self.window.show_all()

    def refresh_list(self, widget, *args):
        search = None
        if isinstance(widget, Gtk.Entry):
            search = widget.get_text()
        self.refresh(search)

    def refresh(self, filter_string=None):
        """ get a new interface and start the progress bar"""
        self.listbox.clear()

        for container in get_containers(filter=filter_string):
            container_info = get_container_info(container['Id'])
            self.listbox.list_containers(container, container_info)

    def closeFetcher(self, widget):
        self.window.hide()

    def show_image_list(self, widget, *args):
        print 'show()'
        self.image_browser.show()


class gtkApplication(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)

    def do_startup(self):
        Gtk.Application.do_startup(self)

        menu = Gio.Menu()
        menu.append("Prefs", "app.new")
        menu.append("About", "app.about")
        menu.append("Quit", "app.quit")
        self.set_app_menu(menu)

        #~ self.set_menubar(menu)
        #~ self.add_simple_action('preferences', self.on_action_preferences_activated)

    def on_action_preferences_activated(self, action, user_data):
        print('will popup preferences dialog')

        #~ self.set_menubar(self.window_menu)
    def do_activate(self):
        # We only allow a single window and raise any existing ones
        #~ if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
        self.main = AppWindow(self)
        self.window = self.main.window
        #~ self.window.set_title('GDocker')
        self.add_window(self.window)
        self.window.show_all()
        self.window.present()

    def add_simple_action(self, name, callback):
        action = Gio.SimpleAction.new(name, None)
        action.connect('activate', callback)
        self.add_action(action)

    # callback function for "quit"
    def quit_cb(self, action, parameter):
        print("You have quit.")
        self.quit()

    def quit(_):
        notify.uninit()
        gtk.main_quit()

    def about(_):
        notify.uninit()
        gtk.main_quit()

if __name__ == '__main__':
    #~ indicator = appindicator.Indicator.new(APPINDICATOR_ID, 'gdcoker.svg', appindicator.IndicatorCategory.CATEGORY_APPLICATION_STATUS)
    indicator = appindicator.Indicator.new(APPINDICATOR_ID, './images/gdocker.png', appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_attention_icon("new-messages-red")
    #~ indicator.set_menu(Gtk.Menu())
        #~ indicator.set_menu(build_menu())
    notify.Notification.new('Gnome docker', 'Gnome Docker applet launched', None).show()
    application = gtkApplication()
    application.run(sys.argv)
    #~ Gtk.main()
