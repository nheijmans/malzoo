############################################################
# Dockerfile to build Malzoo Static File Analysis Framework
# Based on Ubuntu
############################################################

# Set the base image to Ubuntu
FROM ubuntu:16.04

# File Author / Maintainer
MAINTAINER statixs

# Update the repository sources list and install prerequisites
RUN apt-get update && \
apt-get update && \
apt-get install -y vim build-essential python-dev python2 virtualenv libtool bison autoconf python-magic tmux ssdeep git unzip zip python-pip python-bottle libldap-dev libsasl2-dev libldap2-dev libssl-dev wget sudo

#Install YARA
RUN wget https://github.com/VirusTotal/yara/archive/v3.5.0.tar.gz && \
tar -zxf v3.5.0.tar.gz && \
cd yara-3.5.0 && \
./bootstrap.sh && \
./configure && \
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
python setup.py build && \
python setup.py install && \
cd $HOME && \
# Add new non-root user malzoo
useradd -ms /bin/bash malzoo

# Switch to malzoo user
USER malzoo
WORKDIR /home/malzoo

# Download the Malzoo project from GitHub
RUN git clone http://github.com/nheijmans/malzoo.git
WORKDIR /home/malzoo/malzoo

# Setup Virtual Environment
RUN virtualenv malzoo-env && \
/bin/bash -c "source malzoo-env/bin/activate" && \
pip install -r requirements.txt && \
exit

# Copy the configuration file to the correct name
RUN cp config/malzoo.conf.dist config/malzoo.conf && \
# Create folders needed
mkdir attachments storage uploads logs

##################### INSTALLATION END #####################

# Open the port and start malzoo
EXPOSE 1338
WORKDIR /home/malzoo/malzoo
ENTRYPOINT ["python","malzoo.py"]
