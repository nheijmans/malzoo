![Logo](https://cloud.githubusercontent.com/assets/7534191/22924310/eb6d8948-f2a4-11e6-98f6-61125f34f075.png)
# What is MalZoo?
MalZoo is a mass static malware analysis tool that collects the information in a Mongo database
and moves the malware samples to a repository directory based on the first 4 chars of the MD5 hash.
It was build as a internship project to analyze sample sets of 50 G.B.+ (e.g. from http://virusshare.com).

A few examples where it can be used for:
- Use the collected information to visualize the results (e.g. see most used compile languages, packers etc.)
- Gather intell of large open source malware repositories (original intend of the project)
- Monitor a mailbox, analyze the emails and attachments

### Installation information on VM's and bare-metal
For more information on installation and collection of data, check out the [Wiki](https://github.com/nheijmans/malzoo/wiki/Welcome-to-the-MalZoo-wiki!) of this repository. 

### Cloud Serverless deployment
For the deployment in the AWS Cloud with a Serverless architecture, check out the repository [Malzoo Serverless](https://github.com/nheijmans/malzoo_serverless) for an auto-deployment solution.

### Docker container deployment
If you would like to deploy the Malzoo project in a Docker container, you can start very easily with pulling the image from Docker Hub 
```docker pull statixs/malzoo```

And then start a container from there. More instructions further below.

## Information collected
See the wiki page [Information collected](https://github.com/nheijmans/MalZoo/wiki/Collected-data) which data is collected for which sample.

# Installation
See the wiki page [Installation](https://github.com/nheijmans/MalZoo/wiki/Installation-and-configuration) to install MalZoo. The best option is to use the auto installation script bootstrap.sh and once that is done running you only have to execute ```export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH```

# Configuration
After the installation you need to adjust the configuration file malzoo.conf in the config directory. If you are using the Splunk functionality, create a HTTP event collector token in your Splunk instance and copy the token to the configuration file (behind the Splunk part, so you replace the xxx-'es). 

# Usage
See this [Wiki page](https://github.com/nheijmans/MalZoo/wiki/Installation-and-configuration#usage) on how to use Malzoo as an application. Below is the description on how to use the Docker image.

## Docker
Pull the image from Docker Hub with the command 

```
docker pull statixs/malzoo:latest
```

#### Environment list
The environment list contains two items that need to be included, in order for Malzoo to find the virtual environment of Python and to know where the library is for calculating the Fuzzy hashes. The environment file should contain:

```
PYTHONPATH=/home/malzoo/malzoo
LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
```

The first variable makes the virtual environment the Python path, so all the dependencies are found. The second variable is for the Fuzzy hash library to be found correctly.

#### Start a container with persistent logs
If you want to have the logs persistently stored on the host OS, use the following command 

```
docker container run --detach --publish 127.0.0.1:1338:1338/tcp --name malzoo_engine --env-file env.list --rm --volume=./malzoo-logs:/home/malzoo/malzoo/logs/ malzoo:latest
```

This will link the folder malzoo-logs to the Malzoo folder in the container for storing logs. These can then be collected in your favorite data analysis tool. The data of Malzoo is stored in JSON by default. If the data should be send to one of the other receivers like Splunk or MongoDB, you can configure that in the configuration file of Malzoo.

#### Start a container with persistent sample storage
Samples are stored by default in the $HOME/malzoo/storage/ folder. If you want those to be persistent on the host OS, use the following command 

```
docker container run --detach --publish 127.0.0.1:1338:1338/tcp --name malzoo_engine --env-file env.list --rm --volume=./malzoo-samples:/home/malzoo/malzoo/storage/ malzoo:latest
```

The samples are stored within a subfolder, that is named after the first 4 characters of the hash. This option allows for you to build a malware repository persistenly, while using Malzoo as the analysis engine to receive, analyze and store samples. By combining both the persistent logs and samples, the Malzoo engine containers can be scaled up by higher submission rates of samples and stopped in quiet hours.


# Credit
Special thanks goes to the Viper project (http://viper.li). I learned alot about how to automate malware analyse by this project.
Also a big thanks to all the developers of the modules and software used and making it available for everyone to use.

# License
This project is released under the GPL 2.0 License. See the LICENSE for details.
