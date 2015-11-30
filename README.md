#  Open-Event Server

This server which will manage all the data of the event. Backed by a database,
it provides API endpoints to fetch the data, and also to modify/update it.

The database can be a sqlite db file or saved in json itself.

The schema for the database is provided [here](https://github.com/fossasia/open-event/blob/master/DATABASE.md)

The data is provided over the API endpoints as described [here](https://github.com/fossasia/open-event/blob/master/API.md)

# Getting Started

## Install
* Install [VirtualBox][1], choose a version that is compatible with the vagrant version. The current version at the time of writing is `5.0.x` for VirtualBox.
* Install [Vagrant][2] according to the version needed by your system. If you had previously used vagrant and installed with `rubygems` or HomeBrew it will not work with version `5.0.x` of VirtualBox. You need to uninstall any previous version and use the installation file provided on the Vagrant [website][2]. The current version at the time of writing is `1.7.X`, just make sure that Vagrant and VirtualBox are compatible with each other.
* From here you require an active terminal/command prompt at your disposal
* Clone the project
```
git clone git@github.com:fossasia/open-event-orga-server.git
cd open-event-orga-server
```
* Bring up the virtual machine. This will start installation of a ubuntu box within which the server will run with all its components
```
vagrant up
```
If the above command gives you error saying `valid providers not found ...`. Use this command instead
```
vagrant up --provider=virtualbox
```
* You will see a bunch of output related to the provisioning of the virtual machine. Something like below:
```
Bringing machine 'default' up with 'virtualbox' provider...
==> default: Importing base box 'ubuntu/trusty64'...
==> default: Matching MAC address for NAT networking...
==> default: Checking if box 'ubuntu/trusty64' is up to date...
==> default: Preparing network interfaces based on configuration...
    default: Adapter 1: nat
==> default: Forwarding ports...
==> default: Booting VM...
==> default: Waiting for machine to boot. This may take a few minutes...
    default: SSH
    ......
==> default: Preparing to unpack .../libjpeg8_8c-2ubuntu8_amd64.deb ...
==> default: Unpacking libjpeg8:amd64 (8c-2ubuntu8) ...
==> default: Selecting previously unselected package libjbig0:amd64.
==> default: Preparing to unpack .../libjbig0_2.0-2ubuntu4.1_amd64.deb ...
==> default: Unpacking libjbig0:amd64 (2.0-2ubuntu4.1) ...
==> default: Selecting previously unselected package libtiff5:amd64.
==> default: Preparing to unpack .../libtiff5_4.0.3-7ubuntu0.3_amd64.deb ...
    ......
```
Just wait patiently, it will take about 10-15 minutes depending on your computer and the Internet connection. Go sip a coffee in the meantime.

* Once the box is setup up you can enter it by `ssh` in order to examine its contents.
* With Vagrant, the project is automatically synced up, the changes you make to the models and project files are reflected within the vagrant VM.
* Now ssh into the box
```
vagrant ssh
```
* This will bring you to the root directory of the VM. Now do
```
cd /vagrant
```
Now you are inside a synced up copy of the project directory. if you do `ls`, the files within the folder are the same as in your current folder.
* Time to run the app, if the DB migrations went well, then doing this will be okay
```
python create_db.py
```
It should exit normally without raising any errors, if you have any errors, then double check your Database configuration, do `echo $DATABASE_URL` at the command prompt and you should see a string with the Postgres DB url.
```
echo $DATABASE_URL
# Gives something like this below
postgresql://$APP_DB_USER:$APP_DB_PASS@localhost:5432/$APP_DB_NAME
```
If you don't see anything as output, then there is a bug in the provision scripts.
* You can try exporting the `$DATABASE_URL` manually
```
export DATABASE_URL=postgresql://open_event_user:start@localhost:5432/test
```
and then try running `python create_db.py` again
* Finally, fire up
```
python manage.py runserver -h 0.0.0.0 -p 5000
```
* Now your server is up and running. We use 0.0.0.0 as address so that the app binds to all public IPs on the box, so that you can browse it from your host machine. In the `Vagrantfile` we have exposed port 5000 from the guest machine to 8001 so all API calls and HTTP requests must be made via 8001 from the host machine
* To view the admin page go to [127.0.0.1:8001](http://127.0.0.1:8001/) or [localhost:8001](http://localhost:8001/) you should be directed to the admin page automatically.
* Congratulations you have finally made it through the configuration part of the app, now Good Luck Coding :)

## Stack

* Database - Postgres
* Webserver - Nginx
* App server - uwsgi
* Web framework - flask (particularly flask-admin)

## Demo version

[Go to demo version](http://open-event.herokuapp.com/admin/)

## Chat open event orga-server
[![Join the chat at https://gitter.im/fossasia/open-event-orga-server](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/fossasia/open-event-orga-server?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)


## License

This project is currently licensed under the GNU General Public License v3. A
copy of LICENSE.md should be present along with the source code. To obtain the
software under a different license, please contact FOSSASIA.

[1]: https://www.virtualbox.org/wiki/Downloads
[2]: http://www.vagrantup.com/downloads.html
[3]: https://blog.engineyard.com/2014/building-a-vagrant-box
[4]: https://docs.vagrantup.com/v2/getting-started
