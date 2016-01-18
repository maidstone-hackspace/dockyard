#!/usr/bin/env python
# [SNIPPET_NAME: gtk3 listbox example]
# [SNIPPET_CATEGORIES: opengl]
# [SNIPPET_TAGS: touch, gtk3]
# [SNIPPET_DESCRIPTION: add rows to a listbox based on retrieved xml file]
# [SNIPPET_AUTHOR: Oliver Marks ]
# [SNIPPET_LICENSE: GPL]
import os
import requests
import time
from io import StringIO, BytesIO
import subprocess
from lxml.html import parse
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, GLib, Gdk, GdkPixbuf

import gdocker_logs

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

from libs.docker_helper import get_containers, get_container, get_container_name, get_container_forwards, get_container_info
from libs.listbox_rows import ListBoxSelect
DBusGMainLoop(set_as_default=True)



class application_gui:
    """Tutorial 13 custom treeview list boxes"""
    count = 0

    retrieve_job = None

    def __init__(self):
        #load in our glade interface
        xml = Gtk.Builder()
        xml.add_from_file('gdocker.glade')

        #grab our widget using get_object this is the name of the widget from glade, window1 is the default name
        self.window = xml.get_object('winFetcher')

        #load our widgets from the glade file
        self.widgets = {}
        self.widgets['searchentry'] = xml.get_object('entry1')
        self.widgets['searchentry'].connect('changed', self.refresh_list)
        self.widgets['listbox'] = xml.get_object('listbox1')
        self.widgets['progress'] = xml.get_object('listProgress')
        self.widgets['refresh'] = xml.get_object('btnRefresh')
        self.widgets['refresh'].connect('button_press_event', self.refresh_list)
        self.widgets['close'] = xml.get_object('btnClose')
        self.widgets['close'].connect('button_press_event', self.closeFetcher)

        #wrap the listbox so we can reuse the code, pass in the listbox widget to our wrapper class
        self.listbox = ListBoxSelect(self.widgets['listbox'])

        #connect to events, in this instance just quit our application
        self.window.connect('delete_event', Gtk.main_quit)
        self.window.connect('destroy', lambda quit: Gtk.main_quit())

        #show the window else there is nothing to see :)
        self.openFetcher()
        self.refresh()

        # l = gdocker_logs.LogWindow()

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
            print container['Id']
            container_info = get_container_info(container['Id'])
            #~ container_info = docker_client.inspect_container(container['Id'])
            #~ menu_container = gtk.MenuItem(container_info['Name'])
            self.listbox.list_containers(container, container_info)

    def closeFetcher(self, widget):
        self.window.hide()


application = application_gui()

#~ GObject.mainloop.run()
Gtk.main()
