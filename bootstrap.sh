#!/bin/bash
echo "[*] Starting installation of Malzoo & Co. (requirements)..."
sleep 2
cd $HOME

sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -yq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -yq \
    vim build-essential python3-dev python3-venv python3-pip \
    libtool bison flex autoconf automake \
    libmagic-dev libssl-dev libldap-dev libsasl2-dev \
    tmux git unzip zip wget pkg-config

# YARA 4.5.5
echo "[*] Installing YARA 4.5.5..."
wget https://github.com/VirusTotal/yara/archive/v4.5.5.tar.gz
tar -zxf v4.5.5.tar.gz
cd yara-4.5.5
./bootstrap.sh
./configure
make
sudo make install
sudo sh -c 'echo "/usr/local/lib" >> /etc/ld.so.conf'
sudo ldconfig
cd $HOME
sleep 2

# ssdeep 2.14.1
echo "[*] Installing ssdeep 2.14.1..."
wget https://github.com/ssdeep-project/ssdeep/releases/download/release-2.14.1/ssdeep-2.14.1.tar.gz
tar -xf ssdeep-2.14.1.tar.gz
cd ssdeep-2.14.1
./configure
make
sudo make install
sudo ldconfig
cd $HOME
sleep 2

# Malzoo
echo "[*] Setting up Malzoo..."
git clone https://github.com/nheijmans/malzoo.git
cd malzoo
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt -U
deactivate
cp config/malzoo.conf.dist config/malzoo.conf
mkdir -p attachments storage uploads logs
cd $HOME

export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# Cleanup build artifacts
rm -rf v4.5.5.tar.gz yara-4.5.5 ssdeep-2.14.1.tar.gz ssdeep-2.14.1

sleep 2
echo "[+] Done installing!"
