#!/bin/bash
echo "[*] Starting installation of Malzoo & Co. (requirements)..."
sleep 2
cd $HOME
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y vim build-essential python-dev libtool bison autoconf python-magic tmux ssdeep git unzip zip python-pip python-bottle python-requests libldap-dev libsasl2-dev libldap2-dev libssl-dev
#Mongo
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927
echo "deb http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list
sudo apt-get update
sudo apt-get install -y mongodb-org
export LC_ALL=C
sudo service mongod start
sleep 2
#YARA
wget https://github.com/plusvic/yara/archive/v3.4.0.tar.gz
tar -zxf v3.4.0.tar.gz
cd yara-3.4.0
./bootstrap.sh
./configure
make
sudo make install
cd yara-python
python setup.py build
sudo python setup.py install
sudo echo "/usr/local/lib" >> /etc/ld.so.conf
sudo ldconfig
cd $HOME
sleep 2
#SSDeep
wget http://sourceforge.net/projects/ssdeep/files/ssdeep-2.13/ssdeep-2.13.tar.gz/download
mv download ssdeep.tar.gz
tar -xf ssdeep.tar.gz
cd ssdeep-*
./configure
make
sudo make install
cd $HOME
sleep 2
#Pydeep
wget https://github.com/kbandla/pydeep/archive/master.zip
unzip master.zip
cd pydeep-master
python setup.py build
sudo python setup.py install
cd $HOME
sleep 2
#malzoo
git clone https://github.com/nheijmans/MalZoo.git
cd malZoo
sudo pip install -r requirements.txt
cp config/malzoo.conf.dist config/malzoo.conf
cd $HOME
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
sleep 2
rm -r master.zip pydeep-master ssdeep-2.13 ssdeep.tar.gz v3.4.0.tar.gz yara-3.4.0
echo "[+] Done installing!"
