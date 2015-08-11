#What is ZooKeeper?
ZooKeeper is a mass static malware analysis tool that collects the information in a Mongo database
and moves the malware samples to a repository directory based on the first 4 chars of the MD5 hash.
It was build as a internship project to analyze sample sets of 50 G.B.+ (e.g. from http://virusshare.com).

A few examples where it can be used for:
- Use the collected information to visualize the results (e.g. see most used compile languages, packers etc.),
- Add ZooKeeper to cron and analyze a specific directory to collect information,
- Gather intell of large open source malware repositories (original intend of the project)
- Visualize the results that are stored in the Mongo DB by exporting them to Splunk (http://splunk.com). Exclude the strings field tho if you are using the free version!

##Information collected
The following data is being collected from PE files:
- Filename of the sample
- Filetype
- Filesize
- MD5 hash
- SHA-1 hash
- PE hash
- Fuzzy hash
- YARA rules that match
- PE compile time
- Imported DLL's
- PE packer information (if available)
- PE language
- Original filename (if available)
- Strings

######small side note
With ZooKeeper it is quite simple: The more CPU cores you have to analyze the faster the analysis will go. Same goes for disk I/O. Still, I think everyone
that is interested in using ZooKeeper with big amounts of data and does not have a extreme hardware setup can still benefit from it and make large amounts of malware samples searchable
within an acceptable timeframe. 

#Installation
ZooKeeper uses open source programs which needs to be installed before using it. 

###Mongo Database
Make sure to install the Mongo Database first and then the pymongo module. For detailed info
on how to install mongo, see: http://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/#install-mongodb

When you are going to use the mongo CLI and you get a locale error, it might be fixed with this cmd:
```
export LC_ALL=C
```

###YARA
You will also need to install YARA by yourself. Install the packages libtool, bison and autoconf (sudo apt-get install libtool bison autoconf) first and then follow the official documentation (don't forget the python module!).
For details see, http://yara.readthedocs.org/en/v3.3.0/gettingstarted.html#compiling-and-installing-yara <br />
If you are using Ubuntu or debian, prevent this error from happening:
```ImportError: libyara.so.0: cannot open shared object file: No such file or directory```
and add the path /usr/local/lib to the loader configuration file, like so:
```
$ sudo su
$ echo "/usr/local/lib" >> /etc/ld.so.conf
$ ldconfig
```

###SSDeep
And finally, install SSDeep: http://ssdeep.sourceforge.net/usage.html

###Python dependencies
Most of the python libraries that are used can be installed via PIP with:
```pip install -r requirements.txt```

###Other Python dependencies
####Python-magic
The magic library will give an error for some strange reason when installed via PIP so I advice downloading it from Github (https://github.com/ahupp/python-magic)
or if you are using a Debian based distribution via the package manager:
```sudo apt-get update; sudo apt-get install python-magic```

####Pydeep
Install Pydeep with the following commands:
```
wget https://github.com/kbandla/pydeep/archive/master.zip
unzip master.zip
cd pydeep-master
python setup.py build
sudo python setup.py install
```

Then extract the ZIP of ZooKeeper where you want to store the application (e.g. in /opt/) and you are ready to go (well, almost)

#Configuration
After the installation you need to adjust the configuration file app.conf in the config directory. 
Also don't forget to assign the correct number of CPU's, this will be used by the multiprocessing module of Python to start it's processes. 

#Usage
ZooKeeper has two mandatory arguments when you run it. The first one is the directory with malware samples.
The other one is the tag you want to give the group of samples (e.g. 2015-01-01_Malwares). This way you can find
the complete sample set or give a group of specific malware samples a unique label and find these with one search.
Example cmd:
```
python ZooKeeper -d /path/to/samples/ -t projectEvil_samples-2015-01-01
```

#ToDo / Idea's to make ZooKeeper better:  
- [ ] Support other file formats (e.g. PDF, APK, JAR)
- [ ] Directory monitor for live monitoring
- [ ] Add visualisation scripts (with the help of  matplotlib, numPy and Pandas)
- [ ] Add ClamAV module (Works as a seperate tool right now but it increases the time per sample if added to the automated analysis)

#Credit
Special thanks goes to the Viper project (http://viper.li). I learned alot about how to automate malware analyse by this project.
Also a big thanks to all the developers of the modules and software used and making it available for everyone to use.

# License
This project is released under the GPL 2.0 License. See the LICENSE for details.
