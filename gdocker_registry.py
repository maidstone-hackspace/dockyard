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


#https://registry.hub.docker.com/v1/search?q=python
#https://issdocker01.influentialsoftware.com:5000/v2/_catalog
#/v2/_catalog?n=<integer>

def get_registry_images(url, version='v2', search=None):

    final_url = '%s/%s/' % (url, version)
    if search:
        final_url += 'search?q=%s' % search
    else:
        final_url += '_catalog'
    r = requests.get(final_url)
    registry = r.json()
    print registry
    
    if search and version == 'v1':
        for item in registry.get('results'):
            print item
    else:
        for item in registry.get('repositories'):
            print item

class registry_browser():
    def __init__(self):
        #load in our glade interface
        xml = Gtk.Builder()
        xml.add_from_file('gdocker_registry.glade')
        window = xml.get_object('window_registry')
        window.show_all()
    


get_registry_images('https://issdocker01.influentialsoftware.com:5000', version='v2')
get_registry_images('https://registry.hub.docker.com/', version='v1', search='python')
#~ get_registry_images('https://registry.hub.docker.com/', version='v1', search='python')


application = registry_browser()

#~ GObject.mainloop.run()
Gtk.main()

