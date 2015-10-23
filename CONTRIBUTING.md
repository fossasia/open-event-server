# Contributing to our project

Need a push in the right direction?

* [Fork](https://github.com/fossasia/open-event-orga-server/fork) this repo on Github.
* Make sure you have Git, Vagrant and other dependencies installed on your system.
    * [Download Git](https://git-scm.com/downloads)
    * [Download Vagrant](https://www.vagrantup.com/downloads-archive.html)
    * Next download Vagrant. Before that you need to download a virtualbox 
 	   in order to run vagrant.Download a virtualbox of your choice.There 
	   are many boxes available at http://www.vagrantbox.es/.
    * Also create a folder of your choice as your working directory.All the vagrant commands will be run in this             folder.
    * Also you will have to download 'pip'(python package manager) and download nginx and uwsgito use the server.They         can be downloaded using the following commands :
                  sudo apt-get update
                  sudo apt-get install python-pip python-dev nginx
      also uswgi can be downloaded using the following command:
                  pip install uwsgi
* After installing the above dependencies change your working directory which you would like to use as your project directory.
* Run the following command on the terminal
    * Type ```vagrant init```
    * Type ```vagrant up```
    * Type ```vagrant ssh```
    * Run the above commands the new folder you will create as your project folder. Make sure you do not have any            previous Vagrantfile created.
 * Make sure ```vagrant up``` works locally on your machine. If you are not sure, put the output in a [Gist](https://gist.github.com).
* Run the tests on the command line by ```python -m unittest discover```
* Do they run correctly and pass ?. If not, let us know!
* Read the [API Docs](https://githbu.com/fossasia/open-event/blob/master/API.md)
* Do we have docs for each part of the system? If not, patches welcome!
