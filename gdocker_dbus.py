#!/usr/bin/env/python3
# This file is /home/me/test-dbus.py
# Remember to make it executable if you want dbus to launch it
# It works with both Python2 and Python3

from gi.repository import Gtk, GObject
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

from docker import Client
docker_client = Client(base_url='unix://var/run/docker.sock')

def handler(sender=None, test=''):
    print sender
    print "got signal from %r" % sender
    
    
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()
proxy = bus.get_object('org.freedesktop.container', '/org/freedesktop/container')
interface = dbus.Interface(proxy, dbus_interface='org.freedesktop.container')

proxy.connect_to_signal("state_change", handler, dbus_interface="org.freedesktop.container")

#~ bus.add_signal_receiver(handler, dbus_interface = "org.freedesktop.container")



#~ interface.connect_to_signal("state_change", handler, sender_keyword='sender')

print interface.container_stop('c8ba2c6c41a86147eaad3a1959f84e19cdf3b7c520e2cb596782165331be3978')
print interface.container_status('c8ba2c6c41a86147eaad3a1959f84e19cdf3b7c520e2cb596782165331be3978')
#~ print interface.container_start('c8ba2c6c41a86147eaad3a1959f84e19cdf3b7c520e2cb596782165331be3978')
print proxy.get_dbus_method('container_stop', 'org.freedesktop.container.start')



#~ c8ba2c6c41a86147eaad3a1959f84e19cdf3b7c520e2cb596782165331be3978
loop = GObject.MainLoop()
loop.run()

