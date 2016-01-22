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

from libs.docker_helper import get_containers, get_container, get_container_name, get_container_forwards, container_iface, container_proxy

#~ DBusGMainLoop(set_as_default=True)
#~ #TODO look into GDBus instead of dbus

#~ bus = dbus.SessionBus()
#~ container_proxy = bus.get_object('org.freedesktop.container', '/org/freedesktop/container')
#~ container_iface = dbus.Interface(container_proxy, dbus_interface='org.freedesktop.container')
#~ app_name = "Docker"


class ListBoxSelect:
    """ handle the listbox rows dynamically add and remove widgets, and handle download. """
    listbox = None
    gui_rows = {}  # store widgets here so we can destroy them later.

    def __init__(self, listbox, dialog):
        """ pass in list box to manage and connect event"""
        self.listbox = listbox
        self.listbox.connect('row-activated', self.listbox_row_activated)
        self.listbox.connect('button_press_event', self.popup_menu)

        self.menu = Gtk.Menu()
        menu_item1 = Gtk.MenuItem("Show Logs")
        self.menu.append(menu_item1)
        menu_item2 = Gtk.MenuItem("Test")
        self.menu.append(menu_item2)

        self.confirm_dialog = dialog
        #~ self.confirm_dialog.show()
        
        container_proxy.connect_to_signal("state_change", self.update, dbus_interface="org.freedesktop.container")


    def listbox_row_activated(self, listbox, listboxrow):
        """ docker container has been selected so open terminal """
        container_id = listboxrow.get_name()
        container_info = get_container_name(container_id)
        #~ subprocess.call(
            #~ ['gnome-terminal', '--tab', '-e', '''/bin/bash -c "echo 'Connecting to conatiner named %s';sudo docker exec -it xe_container /bin/bash"''' % (container_name,container_name)])
        #~ print 'background'
        
        print container_info
        if container_info['State']['Running']:
            subprocess.call(
                ['gnome-terminal', '--tab', '-e', '''/bin/bash -c "echo 'Connecting to container: %s';
                sudo docker exec -it %s /bin/bash"''' % (container_info['Name'][1:], container_info['Id'])]
            )
        else:
            print "Container not started"  # todo: display error message


    def selection(self, listbox, container, container_info):
        """ docker container has been selected so open terminal """
        print 'called'
        if container_info['State']['Running']:
            subprocess.call(
                ['gnome-terminal', '--tab', '-e', '''/bin/bash -c "echo 'Connecting to container: %s';
                sudo docker exec -it %s /bin/bash"''' % (container_info['Name'][1:], container_info['Id'])]
            )
        else:
            print "Container not started"  # todo: display error message


    def popup_menu(self, widget, event):
        print widget
        print event
        if event.button == 3:
            print 'Right Click'
        self.menu.show_all()
        self.menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

    def list_containers(self, container, container_info):
        """ fill list with all docker containers """
        items = {}
        glade_row = Gtk.Builder()
        glade_row.add_from_file('label.glade')

        items['row'] = glade_row.get_object("list_row")
        items['row'].connect('button_press_event', self.popup_menu)
        #~ items['row'].set_name(container_info['Id'])
        #~ print dir(items['row'])
        #~ items['row'].set_activatable(True)
        #~ items['row'].set_selectable(True)
        #~ items['row'].connect('activate', self.selection, container, container_info)
        #~ items['row'].connect('row-activated', self.selection, container, container_info)

        items['title'] = glade_row.get_object("dockerTitle")
        items['title'].set_label('%s - %s' % (container_info['Name'][1:], container.get('Status')))

        items['image'] = glade_row.get_object("dockerStatus")
        items['image'].set_size_request(64, 64) # = glade_row.get_object("dockerStatus")
        items['uri_container'] = glade_row.get_object("uri_container")
        
        for uri in get_container_forwards(container_info):
            linkbutton = Gtk.LinkButton(uri=uri, label=uri, xalign=0)
            items['uri_container'].pack_start(linkbutton, False, False, 0)

        if container_info['State']['Paused']:
            items['image'].set_from_icon_name("gtk-media-pause", Gtk.IconSize.DIALOG)  # todo: find nice image
        elif container_info['State']['Running']:
            items['image'].set_from_stock("gtk-media-play", Gtk.IconSize.DIALOG)
        else:
            items['image'].set_from_stock("gtk-media-stop", Gtk.IconSize.DIALOG)

        items['switch'] = glade_row.get_object("dockerToggle")
        #~ items['switch'].connect('state-set', self.container_toggle_status, container)
        if container_info['State']['Running']:
            items['switch'].set_active(True)

        items['button'] = glade_row.get_object("dockerRemove")
        items['button'].connect('button_press_event', self.container_delete, items['row'], container)

        self.listbox.add(items['row'])
        items['row'].show_all()
        self.gui_rows[container['Id']] = items

    def is_container_running(self, container):
        if 'Running' in container.get('Status'):
            return False
        return True

    def update(self, container_id):
        print 'container daemon state change'
        print container_id
        #~ state = container_iface.container_status(container_id)
        #~ print state
        #~ self.gui_rows[container['Id']]['switch'].get_state()
        #~ self.gui_rows[container_id]['switch'].set_state(state)

    def container_state_change(self, container_id):

        print 'async callback'
        print container_id
        state = container_iface.container_status(container_id)
        print state

        #~ if state != self.gui_rows[container_id]['switch'].get_active():
        #~ self.gui_rows[container_id]['switch'].set_active(state)
        
        
        #~ self.gui_rows[container_id]['row'].set_sensitive(True)

    def container_change_status(self, container, state):
        if state is False:
            print 'stopping'
            container_iface.container_stop(container.get('Id'), reply_handler=self.container_state_change, error_handler=self.container_state_change)
            return
        print 'starting'
        container_iface.container_start(container.get('Id'), reply_handler=self.container_state_change, error_handler=self.container_state_change)
        return False

    def container_toggle_status(self, widget, test,  container):
        #~ self.gui_rows[container.get('Id')]['row'].set_sensitive(False)
        self.container_change_status(container, widget.get_active())
        return

    def container_delete(self, widget, test,  row, container):
        self.listbox.remove(row)
        print('TODO actually remove the container')
        print row
        print container
        return

    def update_active_progress_bar(self, widgets):
        """ update progress bar until command finished """
        widgets['progress'].pulse()
        if widgets['job'].poll():
            return True
        widgets['progress'].hide()
        return False

    def clear(self):
        """ remove all rows so we can pre-populate"""
        for item in self.gui_rows.values():
            item['row'].destroy()
        self.gui_rows = {}
