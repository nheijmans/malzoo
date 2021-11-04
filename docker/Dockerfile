############################################################
# Dockerfile to build Malzoo Static File Analysis Framework
# Based on Ubuntu
############################################################

# Set the base image to Ubuntu
FROM ubuntu:20.04
 ENV DEBIAN_FRONTEND=noninteractive
# Update the repository sources list and install prerequisites
RUN apt-get update && \
apt-get update && \
apt-get install -y build-essential git pkg-config python3-venv python3-dev python3-pip libtool bison autoconf python-magic ssdeep unzip zip python3-bottle libldap-dev libsasl2-dev libldap2-dev libssl-dev wget sudo
#Install YARA
RUN wget https://github.com/VirusTotal/yara/archive/v4.0.2.tar.gz && \
tar -zxf v4.0.2.tar.gz && \
cd yara-4.0.2 && \
./bootstrap.sh && \./configure && \
make && \
make install && \
echo "/usr/local/lib" >> /etc/ld.so.conf && \
ldconfig && \
cd $HOME && \
#Install SSDeep
wget http://sourceforge.net/projects/ssdeep/files/ssdeep-2.13/ssdeep-2.13.tar.gz/download && \
mv download ssdeep.tar.gz && \
tar -xf ssdeep.tar.gz && \
cd ssdeep-* && \
./configure && \
make && \
make install && \
cd $HOME && \
#Install Pydeep
wget https://github.com/kbandla/pydeep/archive/master.zip && \
unzip master.zip && \
cd pydeep-master && \
python3 setup.py build && \
python3 setup.py install && \
cd $HOME && \
# Add new non-root user malzoo
useradd -ms /bin/bash malzoo
# Switch to malzoo user
USER malzoo
WORKDIR /home/malzoo
# Download the Malzoo project from GitHub
RUN git clone --single-branch --branch migration-python3 http://github.com/nheijmans/malzoo.git
WORKDIR /home/malzoo/malzoo

# Setup Virtual Environment
RUN python3 -m venv malzoo-env && \
/bin/bash -c "source malzoo-env/bin/activate" && \
pip3 install -r requirements.txt && \
exit

# Copy the configuration file to the correct name
RUN cp config/malzoo.conf.dist config/malzoo.conf && \
# Create folders needed
mkdir attachments storage uploads logs

##################### INSTALLATION END #####################

# Open the port and start malzoo
EXPOSE 1338
WORKDIR /home/malzoo/malzoo
ENTRYPOINT ["python3","malzoo.py"]
