# Vagrant

* Navigate to [Vagrant Download Page](http://www.vagrantup.com/downloads.html)
* Click on the proper package for your operating system and architecture, we will be using MAC OSX

![Vagrant-Downloads](https://cloud.githubusercontent.com/assets/9834624/11853310/5e1df64c-a40b-11e5-9d86-a8930e939fd1.png)
![Downloads](https://cloud.githubusercontent.com/assets/9834624/11853313/5e2216c8-a40b-11e5-92d8-d525ba50a4eb.png)
* After clicking on [Universal (32 and 64-bit)](https://releases.hashicorp.com/vagrant/1.7.4/vagrant_1.7.4.dmg) Vagrant will begin to download. Once the download is completed, click on it.

![screen shot 2015-12-16 at 9 43 47 pm](https://cloud.githubusercontent.com/assets/9834624/11860002/5af622e0-a43e-11e5-8292-fabed1a41af1.png)

* Next double-click on Vagrant.pkg to open the package. You will be brought to the Vagrant installer.

![Vagrant-Intro](https://cloud.githubusercontent.com/assets/9834624/11853315/5e2590aa-a40b-11e5-8757-2441db8f0b23.png)

* Click “Continue” to be brought to the next page of the installer.

![Vagrant-Destintaion](https://cloud.githubusercontent.com/assets/9834624/11853317/5e2a1170-a40b-11e5-86c2-5355e7943045.png)

* Select Macintosh HD as the installation destination, then click on “Continue”.

![Vagrant-IType](https://cloud.githubusercontent.com/assets/9834624/11853318/5e5470aa-a40b-11e5-9f28-66222f25b1fe.png)

* Once you have selected the disk where you want to install Vagrant click “Install”.

![Vagrant-Password](https://cloud.githubusercontent.com/assets/9834624/11853325/5e64df30-a40b-11e5-9775-ec3d5d8d8a38.png)

* The Installer will prompt you for your username and password. Then click “Install Software”.

![Vagrant-Summary](https://cloud.githubusercontent.com/assets/9834624/11853320/5e54d70c-a40b-11e5-9483-2fe1a3b51fe6.png)

* If the installation was successful you can close the installer and get ready to setup VirtualBox.

![Vbox-Downloads](https://cloud.githubusercontent.com/assets/9834624/11853321/5e553a3a-a40b-11e5-892b-51b906225cee.png)
* Navigate to the [Virtualbox Download Page](https://www.virtualbox.org/wiki/Downloads).
* Then click on "amd64", right next to the "VirtualBox 5.0.10 for OS X hosts" label.
![VirtualBox-Installer](https://cloud.githubusercontent.com/assets/9834624/11853322/5e5547b4-a40b-11e5-90eb-f2f96cfca33e.png)

* After completing the download open the VirtualBox installer. Click on the “VirtualBox.pkg” icon.

![VirtualBox-RunProgram](https://cloud.githubusercontent.com/assets/9834624/11853327/5e6a30f2-a40b-11e5-9b58-10064b34d843.png)

* The installer will prompt you to run a program to determine if the software can be installed, click “Continue”.

![VirtualBox-Intro](https://cloud.githubusercontent.com/assets/9834624/11853323/5e5ea2dc-a40b-11e5-9a50-ffda4e08297a.png)

* If the program has successfully determined that you can install the software the installer will remain open, press continue. Then select “Macintosh HD” has your installation destination.   Click “Continue”.

![VirtualBox-Intaltype](https://cloud.githubusercontent.com/assets/9834624/11853324/5e621d86-a40b-11e5-9587-298ea5b26a31.png)

* After selecting the destination, click “Install”.

![VirtualBox-Pass](https://cloud.githubusercontent.com/assets/9834624/11853326/5e67b7d2-a40b-11e5-8565-ecf423311c80.png)

* Installer will prompt you for your username and password, then click “Install Software”.

![Virtualbox-summary](https://cloud.githubusercontent.com/assets/9834624/11853329/5e71173c-a40b-11e5-876a-7aca23d3f744.png)

* Once your computer has successfully finished installing Oracle VM VirtualBox you will be directed to the last page of the installer. Click “Close”.

* Open your Terminal application, Terminal’s default location is in your home/applications/utilities folder. You can also open Terminal by searching “Terminal” in spotlight search.

![Terminal-search](https://cloud.githubusercontent.com/assets/9834624/11858953/392f8bb0-a434-11e5-9939-e2de9c14ed7f.png)

* In Terminal, type or copy and paste
```git clone git@github.com:fossasia/open-event-server.git```
after entering commands in Terminal press the "Enter" key.

![Terminal-clone](https://cloud.githubusercontent.com/assets/9834624/11853331/5e75a66c-a40b-11e5-8984-00dd1b57730f.png)
* Then type or copy and paste
```cd open-event-server```
 (cd means change directory)

![Terminal-cd1](https://cloud.githubusercontent.com/assets/9834624/11853330/5e72b952-a40b-11e5-8b58-80f7d1a50b2c.png)

* You will then change into the “open-event-server” directory.

![Terminal-Vagrant](https://cloud.githubusercontent.com/assets/9834624/11853332/5e789fb6-a40b-11e5-876e-ba37e462643d.png)
* In Terminal in the “open-event-server” directory, type
```vagrant up```
to bring up the virtual machine. This will start installation of a ubuntu box within which the server will run with all its components. If after typing “vagrant up” you received an error stating “valid providers not found ….”, type
```vagrant up --provider=virtualbox```
* This step may take a long time depending on your computer and internet connection

![Terminal-cd3](https://cloud.githubusercontent.com/assets/9834624/11853333/5e78ebba-a40b-11e5-9b1a-02ba564c64fb.png)

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
```vagrant ssh```
This will bring you to the root directory of the Virtual Machine.

![Terminal-Appcreate](https://cloud.githubusercontent.com/assets/9834624/11853335/5e7f398e-a40b-11e5-99d3-e3b9662b1819.png)


* Notice that the top of the Terminal window no longer says “bash”. Now type
```cd /vagrant```

![Terminal-Server](https://cloud.githubusercontent.com/assets/9834624/11853337/5e830226-a40b-11e5-8816-4f735307f902.png)


* (optional)In Terminal, type “ls” to view the files of the directory.

![screen shot 2015-12-13 at 7 20 13 pm](https://cloud.githubusercontent.com/assets/9834624/11853339/5e89fcca-a40b-11e5-9b3d-64b0d2429398.png)


* To run the app, type
```python3 create_db.py```
this step should exit normally without raising any errors. If Terminal does report an error type
```echo $DATABASE_URL```
to double check your database configuration.

![screen shot 2015-12-13 at 7 20 31 pm](https://cloud.githubusercontent.com/assets/9834624/11853341/5e8f3f96-a40b-11e5-9d54-76f35af12a05.png)


* Next, type
```python3 manage.py runserver -h 0.0.0.0 -p 5000```

![screen shot 2015-12-13 at 7 22 55 pm](https://cloud.githubusercontent.com/assets/9834624/11853343/5e9cab7c-a40b-11e5-96ad-30df2a3e33a0.png)


* Now your server is up and running. To view the admin page go to [localhost:8001](localhost:8001)
* Congratulations! If you see the admin page you have successfully configured the application!
* If you want to shutdown the server press “CTRL + C”.

![screen shot 2015-12-13 at 7 23 06 pm](https://cloud.githubusercontent.com/assets/9834624/11853345/5eb0e1b4-a40b-11e5-9995-f5bba6255064.png)

![screen shot 2015-12-14 at 5 13 53 pm](https://cloud.githubusercontent.com/assets/9834624/11853344/5ea28ccc-a40b-11e5-82d7-5ce49c2e2991.png)
