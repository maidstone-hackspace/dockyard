#!/usr/bin/env/python3
# This file is /home/me/test-dbus.py
# Remember to make it executable if you want dbus to launch it
# It works with both Python2 and Python3

from gi.repository import Gtk, GObject
import dbus
import dbus.service
import requests
from dbus.mainloop.glib import DBusGMainLoop

from libs.docker_helper import get_registry_images, container_iface
import settings

class registry_browser():
    def __init__(self):
        #load in our glade interface
        xml = Gtk.Builder()
        xml.add_from_file('glade/gdocker_registry.glade')
        self.window = xml.get_object('window_registry')
        self.widget_image_list = xml.get_object('lb_image_list')
        self.registry_list = xml.get_object('cmb_registrys')
        self.pull_progress = xml.get_object('image_progress')
        search_registry_widget = xml.get_object('entry_search')
        search_registry_widget.connect('activate', self.search_registry)

        for registry in settings.registry_list:
            self.registry_list.append_text(registry[0])
        self.registry_list.set_active(0)

        for image in get_registry_images('localhost', version='l', search=''):
            self.add_image(image.get('name'))

        self.menu = Gtk.Menu()
        menu_item1 = Gtk.MenuItem("Pull Images")
        menu_item1.connect('activate', self.pull_image)

        self.menu.append(menu_item1)
        #self.menu.connect('button_press_event', self.container_delete, items['row'], container)
        menu_item2 = Gtk.MenuItem("Start Container")
        self.menu.append(menu_item2)

    def show(self):
        self.window.show_all()

    def docker_message_handler(self, container_id):
        self.pull_progress.stop()
        print 'pull complete callback'
        self.populate()

    def pull_image(self, widget, skip, name):
        # pass the image requested to the dbus daemon for download and respond to the callback
        self.pull_progress.start()
        container_iface.image_pull(name, reply_handler=self.docker_message_handler, error_handler=self.docker_message_handler)


    def search_registry(self, widget):
        for row in self.widget_image_list.get_children():
            row.destroy()

        registry_url = self.registry_list.get_active_text()
        search_value = widget.get_text()
        result = [(reg[0], reg[1]) for reg in settings.registry_list if reg[0] == registry_url]
        if result:
            registry_url, registry_version = result[0]
            for item in get_registry_images(registry_url, version=registry_version, search=search_value):
                self.add_image(item.get('name'))
            self.widget_image_list.show_all()


    def popup_menu(self, widget, event):
        print 'menu'
        if event.button == 3:
            print 'Right Click'
            self.menu.show_all()
            self.menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

    def add_image(self, name):
        row = Gtk.ListBoxRow()
        row.set_activatable(True)
        row.set_selectable(True)
        row.connect('activate', self.popup_menu)
        label = Gtk.Label(name)
        
        layout_box = Gtk.Box()
        
        pull_button = Gtk.Button(label='Pull')
        pull_button.connect('button_press_event', self.pull_image, name)
        
        run_button = Gtk.Button(label='Run')
        run_button.connect('button_press_event', self.pull_image, name)
        
        layout_box.add(label)
        layout_box.add(pull_button)
        layout_box.add(run_button)
        
        
        row.add(layout_box)
        self.widget_image_list.add(row)

#~ application = registry_browser()
#~ Gtk.main()

