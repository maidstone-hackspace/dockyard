#!/usr/bin/env/python3
# Remember to make it executable if you want dbus to launch it
# It works with both Python2 and Python3
import datetime
import sys
from gi.repository import GLib
import threading
import dbus
import json 
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

import docker
from docker import Client
from docker.errors import APIError
docker_client = Client(base_url='unix://var/run/docker.sock')



def container_create(container_params):
    #~ container_params = json.loads(container_params)
    print "\ncreate container %s" % container_params
    try:
        print docker_client.create_container(**container_params)
    except docker.errors.APIError as e:
        print e
        sys.exit(1)
    #~ self.tmp_list()
    #~ self.state_change('start')
    print 'finished'
    return 'finished'


test = {u'command': u'/bin/bash', u'tty': True, u'name': u'gdocker_example_container', u'image': u'buildozer', u'hostname': u'', u'environment': [], u'command': u'', u'volumes': [u'/var/lib/mysql:', u'~/:/root'], u'volumes_from': [], u'detach': False, u'ports': [u'3000:', u'8000:']}

container_create(test)
