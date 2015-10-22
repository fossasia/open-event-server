# Contributing to our project

Need a push in the right direction?

* Fork this repo.
* Make sure you have Git, Vagrant and other dependencies installed.
	* [Download Git](https://git-scm.com/downloads)
	* [Download Vagrant](https://www.vagrantup.com/downloads-archive.html)
   	* Vagrant uses virtualBox as its provider.
   	* [Download VirtualBox](https://www.virtualbox.org/wiki/Downloads)
   	*  Install the dependencies according to your Operating system.
	*  On downloading the above dependencies you will get the appropriate installer or package for your 		  platform.
	* You can then install the dependencies using the standard procedures for your operating system.
	
* On installing the above dependencies change your working directory to the directory you would like to use 
  as your project directory.
* On doing so run the following commands on the terminal:
	* ```vagrant init hashicorp/precise32```
	* ```vagrant up```
	* ```vagrant ssh```
* Make sure ```vagrant up``` works locally on your machine. If you are not sure, put the output in a [Gist](https://gist.github.com).
* Go to ```http://192.168.33.10``` , as specified by the Vagrant file.Put the output in a Gist.
* Run the tests on the command line using ```python -m unittest discover```
* Do they run correctly and pass? If not,put the output in a [Gist](https://gist.github.com).
* Read the [API docs](https://github.com/fossasia/open-event/blob/master/API.md).
* Read the docs. Do we have some for each part of the system? If not, patches welcome!
