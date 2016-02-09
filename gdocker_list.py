#!/usr/bin/env python
# [SNIPPET_NAME: gtk3 listbox example]
# [SNIPPET_CATEGORIES: opengl]
# [SNIPPET_TAGS: touch, gtk3]
# [SNIPPET_DESCRIPTION: add rows to a listbox based on retrieved xml file]
# [SNIPPET_AUTHOR: Oliver Marks ]
# [SNIPPET_LICENSE: GPL]


import gi
#~ gi.require_version('Gtk', '3.0')
#~ gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify

from settings import APPINDICATOR_ID
from libs.docker_helper import get_containers, get_container, get_container_info, get_container_forwards
from libs.listbox_rows import ListBoxSelect
from gdocker_registry import registry_browser


class application_gui:
    """Tutorial 13 custom treeview list boxes"""
    count = 0

    retrieve_job = None

    def __init__(self):
        # load in our glade interface
        xml = Gtk.Builder()
        xml.add_from_file('glade/gdocker.glade')

        self.image_browser = registry_browser()

        # grab our widget using get_object this is the name of the widget from glade, window1 is the default name
        self.window = xml.get_object('root_window')

        # load our widgets from the glade file
        self.widgets = {}
        self.widgets['searchentry'] = xml.get_object('search_containers')
        self.widgets['searchentrycompletion'] = xml.get_object('search_container_completion')
        self.widgets['searchentry'].set_completion(self.widgets['searchentrycompletion'])

        self.widgets['open_registry'] = xml.get_object('btn_open_registry')
        self.widgets['open_registry'].connect('button_press_event', self.show_image_list)
        self.widgets['searchentry'].connect('changed', self.refresh_list)
        self.widgets['listbox'] = xml.get_object('listbox1')
        self.widgets['progress'] = xml.get_object('listProgress')
        self.widgets['refresh'] = xml.get_object('btnRefresh')
        self.widgets['message_dialog'] = xml.get_object('dialog_confirm')
        self.widgets['refresh'].connect('button_press_event', self.refresh_list)
        self.widgets['close'] = xml.get_object('btnClose')
        self.widgets['close'].connect('button_press_event', self.closeFetcher)

        # wrap the listbox so we can reuse the code, pass in the listbox widget to our wrapper class
        self.listbox = ListBoxSelect(self.widgets['listbox'], self.widgets['message_dialog'])

        # connect to events, in this instance just quit our application
        self.window.connect('delete_event', Gtk.main_quit)
        self.window.connect('destroy', lambda quit: Gtk.main_quit())

        # show the window else there is nothing to see :)
        self.openFetcher()
        self.refresh()

    def openFetcher(self):
        self.window.show_all()

    def refresh_list(self, widget, *args):
        search = None
        if isinstance(widget, Gtk.Entry):
            search = widget.get_text()
        self.refresh(search)

    def refresh(self, filter_string=None):
        """ get a new xml and start the progress bar"""
        self.listbox.clear()

        for container in get_containers(filter=filter_string):
            container_info = get_container_info(container['Id'])
            self.listbox.list_containers(container, container_info)

    def closeFetcher(self, widget):
        self.window.hide()

    def show_image_list(self, widget, *args):
        print 'show()'
        self.image_browser.show()

#~ def quit(_):
    #~ notify.uninit()
    #~ gtk.main_quit()

if __name__ == '__main__':
    #~ indicator = appindicator.Indicator.new(APPINDICATOR_ID, 'gdcoker.svg', appindicator.IndicatorCategory.CATEGORY_APPLICATION_STATUS)
    indicator = appindicator.Indicator.new(APPINDICATOR_ID, './images/gdocker.png', appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_attention_icon("new-messages-red")
    indicator.set_menu(Gtk.Menu())
        #~ indicator.set_menu(build_menu())
    notify.Notification.new('Gnome docker', 'Gnome Docker applet launched', None).show()
    application = application_gui()
    Gtk.main()
