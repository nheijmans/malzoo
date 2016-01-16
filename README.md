#What is MalZoo?
MalZoo is a mass static malware analysis tool that collects the information in a Mongo database
and moves the malware samples to a repository directory based on the first 4 chars of the MD5 hash.
It was build as a internship project to analyze sample sets of 50 G.B.+ (e.g. from http://virusshare.com).

A few examples where it can be used for:
- Use the collected information to visualize the results (e.g. see most used compile languages, packers etc.),
- Add MalZoo to cron and analyze a specific directory to collect information,
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
- Imphash
- YARA rules that match
- PE compile time
- Imported DLL's
- PE packer information (if available)
- PE language
- Original filename (if available)
- Strings

######small side note
With MalZoo it is quite simple: The more CPU cores you have to analyze the faster the analysis will go. Same goes for disk I/O. Still, I think everyone
that is interested in using MalZoo with big amounts of data and does not have a extreme hardware setup can still benefit from it and make large amounts of malware samples searchable
within an acceptable timeframe. 

#Installation
See the Wiki [Installation](https://github.com/nheijmans/MalZoo/wiki/Installation-and-configuration) page

#ToDo / Idea's to make MalZoo better:  
- [ ] Support other file formats (e.g. PDF, APK, JAR)
- [x] Directory monitor for live monitoring
- [ ] Add visualisation scripts (with the help of  matplotlib, numPy and Pandas)
- [ ] Add ClamAV module (Works as a seperate tool right now but it increases the time per sample if added to the automated analysis)

#Credit
Special thanks goes to the Viper project (http://viper.li). I learned alot about how to automate malware analyse by this project.
Also a big thanks to all the developers of the modules and software used and making it available for everyone to use.

# License
This project is released under the GPL 2.0 License. See the LICENSE for details.
