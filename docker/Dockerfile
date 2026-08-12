############################################################
# Dockerfile to build Malzoo Static File Analysis Framework
# Based on Ubuntu 24.04 LTS
############################################################

# Set the base image to Ubuntu
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# Update the repository sources list and install prerequisites
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    git \
    pkg-config \
    python3-venv \
    python3-dev \
    python3-pip \
    libtool \
    bison \
    flex \
    autoconf \
    automake \
    libmagic-dev \
    libssl-dev \
    libldap-dev \
    libsasl2-dev \
    wget \
    unzip \
    zip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install YARA 4.5.5
RUN wget https://github.com/VirusTotal/yara/archive/v4.5.5.tar.gz && \
    tar -zxf v4.5.5.tar.gz && \
    cd yara-4.5.5 && \
    ./bootstrap.sh && \
    ./configure && \
    make && \
    make install && \
    echo "/usr/local/lib" >> /etc/ld.so.conf && \
    ldconfig && \
    cd / && \
    rm -rf v4.5.5.tar.gz yara-4.5.5

# Install ssdeep 2.14.1
RUN wget https://github.com/ssdeep-project/ssdeep/releases/download/release-2.14.1/ssdeep-2.14.1.tar.gz && \
    tar -xf ssdeep-2.14.1.tar.gz && \
    cd ssdeep-2.14.1 && \
    ./configure && \
    make && \
    make install && \
    ldconfig && \
    cd / && \
    rm -rf ssdeep-2.14.1.tar.gz ssdeep-2.14.1

# Add non-root user
RUN useradd -ms /bin/bash malzoo

# Switch to malzoo user
USER malzoo
WORKDIR /home/malzoo

# Download the Malzoo project from GitHub
RUN git clone --single-branch --branch master https://github.com/nheijmans/malzoo.git
WORKDIR /home/malzoo/malzoo

# Setup Virtual Environment and install dependencies
RUN python3 -m venv malzoo-env && \
    . malzoo-env/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Copy the configuration file and create required directories
RUN cp config/malzoo.conf.dist config/malzoo.conf && \
    mkdir -p attachments storage uploads logs

##################### INSTALLATION END #####################

# Set environment variables
ENV PYTHONPATH=/home/malzoo/malzoo
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
ENV PATH="/home/malzoo/malzoo/malzoo-env/bin:$PATH"

# Open the port and start malzoo
EXPOSE 1338
WORKDIR /home/malzoo/malzoo
ENTRYPOINT ["python3", "malzoo.py"]
