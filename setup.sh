#!/bin/bash

cp gdocker.desktop /usr/share/applications/

cp images/24x24/gdocker.png /usr/share/icons/gnome/24x24/apps/
cp images/32x32/gdocker.png /usr/share/icons/gnome/32x32/apps/
cp images/48x48/gdocker.png /usr/share/icons/gnome/48x48/apps/
cp images/128x128/gdocker.png /usr/share/icons/gnome/128x128/apps/

cp images/24x24/gdocker.png /usr/share/icons/hicolor/24x24/apps/
cp images/32x32/gdocker.png /usr/share/icons/hicolor/32x32/apps/
cp images/48x48/gdocker.png /usr/share/icons/hicolor/48x48/apps/
cp images/128x128/gdocker.png /usr/share/icons/hicolor/128x128/apps/



cp gdocker_daemon.py /usr/local/bin/gdocker_daemon.py
cp gdocker_daemon.service /usr/share/dbus-1/services/gdocker_daemon.service

mkdir -p /usr/local/share/gdocker
cp gdocker /usr/local/bin/gdocker
cp -R * /usr/local/share/gdocker
chmod +x /usr/local/share/gdocker/gdocker_daemon
chmod +x /usr/local/share/gdocker/gdocker
chmod +x /usr/local/bin/gdocker

desktop-file-install /usr/share/applications/gdocker.desktop
xdg-desktop-menu forceupdate


desktop-file-validate gdocker.desktop

update-desktop-database
