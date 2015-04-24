#!/bin/bash
echo "Installing global dependencies"
sudo apt-get install python2.7 python-virtualenv wget tar make libyaml-dev

echo "Creating and entering virtualenv (mmlf_venv)"
python2 -m virtualenv --always-copy mmlf_venv
source mmlf_venv/bin/activate

echo "DEBUG: " $PS1 

echo "Building local sip and PyOt4"
cd mmlf_venv
mkdir packages
cd packages

echo "-- Downloading sip"
wget http://sourceforge.net/projects/pyqt/files/sip/sip-4.16.7/sip-4.16.7.tar.gz
tar xfz sip-4.16.7.tar.gz
cd sip-4.16.7
echo "-- Building sip"
../../bin/python configure.py --incdir=../../include 
make || exit $?
echo "-- Installing sip"
make install || exit $?
cd ..

echo "-- Downloading PyQt4"
wget http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.11.3/PyQt-x11-gpl-4.11.3.tar.gz
tar xfz PyQt-x11-gpl-4.11.3.tar.gz
cd PyQt-x11-gpl-4.11.3
echo "-- Building PyQt4"
../../bin/python configure.py --confirm-license 
make || exit $?
echo "-- Installing PyQt4"
make install || exit $?
cd ../../../

echo "Installing MMLF dependencies"
mmlf_venv/bin/pip install pyyaml numpy 
mmlf_venv/bin/pip install matplotlib scipy

echo "Installing libANN and scikits.ann"
cd mmlf_venv/packages

echo "-- Downloading libANN"
wget http://www.cs.umd.edu/~mount/ANN/Files/1.1.2/ann_1.1.2.tar.gz
tar xfz ann_1.1.2.tar.gz
cd ann_1.1.2
echo "-- Building libANN"
make linux-g++ || exit $?
cp -r bin/ lib/ include/ ../../
cd ..

echo "-- Downloading scikits.ann"
wget https://pypi.python.org/packages/source/s/scikits.ann/scikits.ann-0.2.dev-r803.tar.gz#md5=a0380cdc31fd705c15eb50f483bbe5fb
tar xfz scikits.ann-0.2.dev-r803.tar.gz
cd scikits.ann-0.2.dev-r803

# Comment out all NumpyTest things
sed '/NumpyTest/s/^/#/g' -i ./scikits/ann/__init__.py
sed '/NumpyTest/s/^/#/g' -i ./scikits/ann/tests/test_ann.py

echo "-- Building scikits.ann"
ANN_LIB=../../lib ANN_INCLUDE=../../include ../../bin/python setup.py build_ext --inplace build test || exit $?
../../bin/python setup.py install

echo "Done"

