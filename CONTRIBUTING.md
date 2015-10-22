# Contributing to our project

Need a push in the right direction?

* [Fork](https://github.com/fossasia/open-event-orga-server/fork) this repo on Github.
* Make sure you have Git, Vagrant and other dependencies installed on your system.
    * [Download Git](https://git-scm.com/downloads)
    * [Download Vagrant](https://www.vagrantup.com/downloads-archive.html)
    * Vagrant uses virtualBox as its provider.
    * [Download VirtualBox](https://www.virtualbox.org/wiki/Downloads)
    * Install the dependencies according to your Operating system.
* After installing the above dependencies change your working directory which you would like to use as your project directory.
* Run the following command on the terminal
    * Type ```vagrant init```
    * Type ```vagrant up```
    * Type ```vagrant ssh```
* Make sure ```vagrant up``` works locally on your machine. If you are not sure, put the output in a [Gist](https://gist.github.com).
* Run the tests on the command line by ```python -m unittest discover```
* Do they run correctly and pass ?. If not, let us know!
* Read the [API Docs](https://github.com/fossasia/open-event/blob/master/API.md)
* Do we have docs for each part of the system? If not, patches welcome!