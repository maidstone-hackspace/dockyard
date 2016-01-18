GDocker
-------

GDocker is a gtk front end to managing your containers, its aim is to allow you to start stop and debug your container with ease.

To try out this project you will need to have python-glib and python-gi installed then clone the repo.


Run the daemon first this is used by the front end to change the container states with out blocking the gui.

    python gdocker_daemon.py

Now run the desktop app

    python gdocker.py
