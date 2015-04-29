#!/bin/bash
echo "Installing global dependencies"
sudo apt-get install python2.7 python-virtualenv wget tar make

echo "Creating and entering virtualenv (mmlf_venv)"
#python2 -m virtualenv --always-copy mmlf_venv
#source mmlf_venv/bin/activate

echo "DEBUG: " $PS1 

echo "Building local sip and PyOt4"
#cd mmlf_venv
mkdir packages
cd packages

echo "-- Downloading sip"
wget http://sourceforge.net/projects/pyqt/files/sip/sip-4.16.7/sip-4.16.7.tar.gz
tar xfz sip-4.16.7.tar.gz
cd sip-4.16.7
echo "-- Building sip"
python configure.py --incdir=../../include 
make || exit $?
echo "-- Installing sip"
sudo make install || exit $?
cd ..

echo "-- Downloading PyQt4"
wget http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.11.3/PyQt-x11-gpl-4.11.3.tar.gz
tar xfz PyQt-x11-gpl-4.11.3.tar.gz
cd PyQt-x11-gpl-4.11.3
echo "-- Building PyQt4"
python configure.py --confirm-license 
make || exit $?
echo "-- Installing PyQt4"
sudo make install || exit $?
cd ../../../

echo "Installing MMLF dependencies"
sudo pip install pyyaml matplotlib numpy
sudo pip install scipy

echo "Done"

