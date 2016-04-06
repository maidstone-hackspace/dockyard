#!/bin/bash

cp ./dockyard.desktop /usr/share/applications/

cp images/24x24/dockyard.png /usr/share/icons/gnome/24x24/apps/
cp images/32x32/dockyard.png /usr/share/icons/gnome/32x32/apps/
cp images/48x48/dockyard.png /usr/share/icons/gnome/48x48/apps/
cp images/128x128/dockyard.png /usr/share/icons/gnome/128x128/apps/
cp images/scalable/dockyard.svg /usr/share/icons/gnome/scalable/apps/

cp images/24x24/dockyard.png /usr/share/icons/hicolor/24x24/apps/
cp images/32x32/dockyard.png /usr/share/icons/hicolor/32x32/apps/
cp images/48x48/dockyard.png /usr/share/icons/hicolor/48x48/apps/
cp images/128x128/dockyard.png /usr/share/icons/hicolor/128x128/apps/
cp images/scalable/dockyard.svg /usr/share/icons/hicolor/scalable/apps/


cp dockyard_daemon.py /usr/local/bin/dockyard_daemon.py
cp dockyard.service /usr/share/dbus-1/services/dockyard.service

mkdir -p /usr/local/share/dockyard
cp dockyard /usr/local/bin/dockyard
cp -R * /usr/local/share/dockyard
chmod +x /usr/local/share/dockyard/dockyard_daemon
chmod +x /usr/local/share/dockyard/dockyard
chmod +x /usr/local/bin/dockyard

desktop-file-install /usr/share/applications/dockyard.desktop
xdg-desktop-menu forceupdate


desktop-file-validate dockyard.desktop

update-desktop-database
