#$current_folder = `pwd`

mkdir -p /opt/xdg-apps/dockyard/appdir
mkdir -p /opt/xdg-apps/dockyard/appdir/files
mkdir -p /opt/xdg-apps/dockyard/appdir/files/bin
mkdir -p /opt/xdg-apps/dockyard/appdir/export
cp ./metadata /opt/xdg-apps/dockyard/appdir/
cp ./dockyard /opt/xdg-apps/dockyard/appdir/files/bin/
cp -R ../../* /opt/xdg-apps/dockyard/appdir/files
chmod a+x /opt/xdg-apps/dockyard/appdir/files/bin/dockyard

#setup complete now lets build 
cd /opt/xdg-apps/dockyard/


xdg-app --user remote-add --no-gpg-verify tutorial-repo repo
xdg-app build-export repo appdir
xdg-app build-finish appdir --socket=x11 --share=network --command=dockyard
xdg-app --user uninstall org.digitaloctave.Dockyard
xdg-app --user install tutorial-repo org.digitaloctave.Dockyard
xdg-app run org.digitaloctave.Dokcyard

#restore to the previous path
cd $PWD
