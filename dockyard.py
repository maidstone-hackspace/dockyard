#!/usr/bin/env python

import os
import sys
import gi
import ConfigParser

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
from libs.utils import return_browsers, test_in_group
from libs.core import interface

class AppWindow(object):
    """Tutorial 13 custom treeview list boxes"""
    count = 0
    retrieve_job = None

    def __init__(self, app):
        self.image_browser = image_browser()

        # grab our widget using get_object this is the name of the widget from glade, window1 is the default name
        self.window = interface.get_object('root_window')
        self.window.set_wmclass ('Dockyard', 'Dockyard')
        self.window.set_title('Dockyard')
        self.window.set_application(app)
        self.window_about = interface.get_object('aboutdialog1')
        self.window_prefs = interface.get_object('prefs_window')
        self.window_menu = interface.get_object('root_window_menu')
        self.window_menu_prefs = interface.get_object('root_window_prefs')

        self.window_prefs.connect('delete-event', self.hide_window)

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
        #~ self.widgets['refresh'] = interface.get_object('btnRefresh')
        self.widgets['message_dialog'] = interface.get_object('dialog_confirm')
        #~ self.widgets['refresh'].connect('button_press_event', self.refresh_list)

        # wrap the listbox so we can reuse the code, pass in the listbox widget to our wrapper class
        self.listbox = ListBoxSelect(self.widgets['listbox'], self.widgets['message_dialog'])

        # connect to events, in this instance just quit our application
        self.window.connect('delete_event', Gtk.main_quit)
        self.window.connect('destroy', lambda quit: Gtk.main_quit())
        if container_proxy:
            container_proxy.connect_to_signal("state_change", self.refresh_list, dbus_interface="org.freedesktop.container")

        # show the window else there is nothing to see :)
        self.openFetcher()
        self.refresh()

    def preferences_closed(self, widget, *data):
        self.window_prefs.hide() 

    def hide_window(self, widget, *data):
        self.window_prefs.hide() 
        return True


    def populate_prefs(self):
        filename = os.path.expanduser('~/.dockyard.cfg')
        config = ConfigParser.SafeConfigParser({
            'browser': 'firefox',
            'docker_api_url': 'unix://var/run/docker.sock'
        })
        config.read(['dockyard.cfg', os.path.expanduser('~/.dockyard.cfg')])
        if not config.has_section('settings'):
            config.add_section('settings')


        self.prefs_select_browser = interface.get_object('cmb_prefs_select_browser')
        model = self.prefs_select_browser.get_model()
        model.clear()
        for browser, path in return_browsers():
            self.prefs_select_browser.append_text(browser)
        self.prefs_select_browser.set_active(0)
        self.window_prefs.show_all()
        
        browser = self.prefs_select_browser.get_active() or 'firefox'

        config.set('settings', 'browser', browser)
        # tmp write out prefs
        with open(filename, 'wb') as configfile:
            config.write(configfile)

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

    def show_image_list(self, widget, *args):
        print 'show()'
        self.image_browser.show()


class gtkApplication(Gtk.Application):
    def __init__(self, *args, **kwargs):
        Gtk.Application.__init__(self)
        self.window = None

    def do_startup(self):
        Gtk.Application.do_startup(self)

        menu = Gio.Menu()
        menu.append("Preferences", "app.preferences")
        menu.append("About", "app.about")
        menu.append("Quit", "app.quit")
        self.set_app_menu(menu)

        self.add_simple_action('preferences', self.on_action_preferences_activated)
        self.add_simple_action('about', self.on_action_about_activated)
        self.add_simple_action('quit', self.on_action_quit_activated)

    def do_activate(self):
        if not self.window:
            self.main = AppWindow(self)
            self.window = self.main.window
        self.window.present()

    def add_simple_action(self, name, callback):
        action = Gio.SimpleAction.new(name, None)
        action.connect('activate', callback)
        self.add_action(action)

    def on_action_preferences_activated(self, action, user_data):
        self.main.populate_prefs()

    def on_action_about_activated(self, action, user_data):
        self.main.window_about.show()

    def on_action_quit_activated(self, action, user_data):
        notify.uninit()
        self.quit()

if __name__ == '__main__':
    #~ indicator = appindicator.Indicator.new(APPINDICATOR_ID, 'gdcoker.svg', appindicator.IndicatorCategory.CATEGORY_APPLICATION_STATUS)
    indicator = appindicator.Indicator.new(APPINDICATOR_ID, './images/dockyard.png', appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_attention_icon("new-messages-red")
    
    #test the user is in the docker group, bail if not or ignore if not linux
    test_in_group()

    notify.Notification.new('Dockyard', 'Dockyard applet launched', None).show()
    application = gtkApplication()
    application.run(sys.argv)

