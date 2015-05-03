#!/bin/bash
echo "Installing global dependencies"
sudo apt-get install python2.7 wget tar make libyaml-dev swig

#echo "Creating and entering virtualenv (mmlf_venv)"
#python2 -m virtualenv --always-copy mmlf_venv
#source mmlf_venv/bin/activate

echo "Building local sip and PyOt4"
#cd mmlf_venv
mkdir packages
cd packages

echo "-- Downloading sip"
wget http://sourceforge.net/projects/pyqt/files/sip/sip-4.16.7/sip-4.16.7.tar.gz
tar xfz sip-4.16.7.tar.gz
cd sip-4.16.7
echo "-- Building sip"
python2 configure.py --incdir=../../include 
make || exit $?
echo "-- Installing sip"
sudo make install || exit $?
cd ..

echo "-- Downloading PyQt4"
wget http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.11.3/PyQt-x11-gpl-4.11.3.tar.gz
tar xfz PyQt-x11-gpl-4.11.3.tar.gz
cd PyQt-x11-gpl-4.11.3
echo "-- Building PyQt4"
python2 configure.py --confirm-license 
make || exit $?
echo "-- Installing PyQt4"
sudo make install || exit $?
cd ../../

echo "Installing MMLF dependencies"
python2 -m pip install pyyaml numpy 
python2 -m pip install matplotlib scipy

echo "Installing libANN and scikits.ann"
cd packages

echo "-- Downloading libANN"
wget http://www.cs.umd.edu/~mount/ANN/Files/1.1.2/ann_1.1.2.tar.gz
tar xfz ann_1.1.2.tar.gz
cd ann_1.1.2
echo "-- Building libANN"
make linux-g++ || exit $?
sudo cp -r bin/ lib/ include/ /
cd ..

echo "-- Downloading scikits.ann"
wget https://pypi.python.org/packages/source/s/scikits.ann/scikits.ann-0.2.dev-r803.tar.gz#md5=a0380cdc31fd705c15eb50f483bbe5fb
tar xfz scikits.ann-0.2.dev-r803.tar.gz
cd scikits.ann-0.2.dev-r803

# Comment out all NumpyTest things
sed '/NumpyTest/s/^/#/g' -i ./scikits/ann/__init__.py
sed '/NumpyTest/s/^/#/g' -i ./scikits/ann/tests/test_ann.py

echo "-- Building scikits.ann"
ANN_LIB=/lib ANN_INCLUDE=/include python2 setup.py build_ext --inplace build test || exit $?
sudo python2 setup.py install

echo "Done"

