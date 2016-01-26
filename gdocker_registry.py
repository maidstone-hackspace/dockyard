#!/usr/bin/env/python3
# This file is /home/me/test-dbus.py
# Remember to make it executable if you want dbus to launch it
# It works with both Python2 and Python3

from gi.repository import Gtk, GObject
import dbus
import dbus.service
import requests
from dbus.mainloop.glib import DBusGMainLoop

from docker import Client
docker_client = Client(base_url='unix://var/run/docker.sock')
import settings

#https://registry.hub.docker.com/v1/search?q=python
#https://issdocker01.influentialsoftware.com:5000/v2/_catalog
#/v2/_catalog?n=<integer>

def get_registry_images(url, version='v2', search=None):
    print search
    dangling_image = 0
    if version == 'l':
        results = docker_client.images()
        for item in results:
            labels = item.get('Labels')
            if item.get('RepoTags') == ['<none>:<none>']:
                dangling_image += 1
                continue
            if search in item.get('RepoTags')[0]:
                yield {'name': item.get('RepoTags')[0]}
    else:

        final_url = '%s/%s/' % (url, version)
        if search:
            final_url += 'search?q=%s' % search
        else:
            final_url += '_catalog'
        r = requests.get(final_url)
        registry = r.json()
        
        #~ if search and version == 'v1':
        for item in registry.get('results' if version=='v1' else 'repositories'):
            print item
            yield item
        #~ else:
            #~ for item in registry.get('repositories'):
                #~ print item

class registry_browser():
    def __init__(self):
        #load in our glade interface
        xml = Gtk.Builder()
        xml.add_from_file('glade/gdocker_registry.glade')
        window = xml.get_object('window_registry')
        self.widget_image_list = xml.get_object('lb_image_list')
        self.registry_list = xml.get_object('cmb_registrys')
        search_registry_widget = xml.get_object('entry_search')
        search_registry_widget.connect('activate', self.search_registry)
        
        
        for registry in settings.registry_list:
            self.registry_list.append_text(registry[0])
        self.registry_list.set_active(0)
        
        for image in get_registry_images('localhost', version='l', search=''):
            self.add_image(image.get('name'))
        
        window.show_all()

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

    def add_image(self, name):
        row = Gtk.ListBoxRow()
        label = Gtk.Label(name)
        row.add(label)
        self.widget_image_list.add(row)

application = registry_browser()
Gtk.main()

