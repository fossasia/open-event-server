# Google Compute Engine

## Initialization

Under this we will create a Project using Google Cloud Platform, that will hold your docker container on a machine.

* Go to Google Cloud Platform [website](https://console.cloud.google.com) and login with your Google account.

* This Application needs Compute Engine for deployment. To use Compute Engine, you need to enable Billing on your account. As soon as you are done with that(Entering Billing info. etc.), you will be taken to your Dashboard.

<img width="1440" alt="dashboard-screen" src="https://cloud.githubusercontent.com/assets/7330961/19032491/af2cd074-8977-11e6-9a03-28db71d0080c.png">

* Create a new project on GCP that will hold all info related to your project. Compute Engine will take a minute to intialize on your project once you are done.[Get a ☕️]

<img width="788" alt="new-project" src="https://cloud.githubusercontent.com/assets/7330961/19032660/d1c8162e-8978-11e6-9ff7-869a740ae2c0.png">

* After creating a new Project, and on the Compute engine home, Create a new Compute Engine Instance.

<img width="409" alt="create-instance" src="https://cloud.githubusercontent.com/assets/7330961/19032815/81ca71f2-8979-11e6-9dbc-dbd6fa9526f6.png">

* You also need to do some configuration for the Machine or GCE Instance

<img width="792" alt="instance-config" src="https://cloud.githubusercontent.com/assets/7330961/19032835/9b834092-8979-11e6-9052-4fba991443ad.png">

* We'll take Ubuntu 16.04LTS as the Base disk with the Default disk size or you can use SSD if willing to. You can choose any zone you want, but choosing nearest geagraphical location will serve better ssh and ping times. You can use any amount of memory or RAM her, default would be good enough. You also need to Allow HTTP and HTTPS traffic.

* After you are done with configuring the Instance, click on Create, this will take some more minutes.[Get a 🍩]

* Once this is done, and you are on instances page, an Ephemeral IP is allotted to your Instance which will be used to connect to your instance.
<img width="710" alt="screen shot 2016-10-03 at 15 06 38" src="https://cloud.githubusercontent.com/assets/7330961/19033621/eeb10076-897c-11e6-95f2-0471a4d372fd.png">

* Finally, Go to the Metadata section of your project and add an SSH key. For that,
```sh
pbcopy < ~/.ssh/id_rsa.pub
```
<img width="252" alt="screen shot 2016-10-03 at 15 11 33" src="https://cloud.githubusercontent.com/assets/7330961/19033723/8527d142-897d-11e6-987e-26eb2e559b6c.png">
<img width="970" alt="screen shot 2016-10-03 at 15 12 51" src="https://cloud.githubusercontent.com/assets/7330961/19033785/cfdb5934-897d-11e6-9e8e-7ff540fb52e3.png">

* If you don't already have an ssh key, please look at this [page](https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) here by Github.

* Once you have generated and added an SSH key to the ssh-agent and your account, Click Save on the Metadata page. The Username is auomatically dislplayed oin front of it. This would be the username we will be using to connect to the Instance.
<img width="666" alt="screen shot 2016-10-03 at 16 55 24" src="https://cloud.githubusercontent.com/assets/7330961/19035913/2ddaa8b2-898a-11e6-871b-a0063855f53a.png">

## Setting up Docker on our Instance

* To setup Docker on the Instance, we need to ssh into the GCE Machine. Open up a Terminal emulator & replace your own login creds, username & IP for your Instance
```sh
ssh -i ~/.ssh/id_rsa <USERNAME>@<EPHEMERAL IP>
```

* After this you will be logged in to the Instance.
<img width="1440" alt="screen shot 2016-10-03 at 15 30 37" src="https://cloud.githubusercontent.com/assets/7330961/19033878/4be6469c-897e-11e6-8ae5-2e30be6ab7f3.png">

* After Logging in to the Instance use these Commands(Don't forget to replace the IP Address):
```sh
sudo apt update && sudo apt install language-pack-en
echo 'export SERVER_NAME=<YOUR EPHEMERAL IP ALLOTTED GOES HERE>' | sudo tee --append /etc/environment > /dev/null
echo 'export LC_ALL="en_US.UTF-8"' | sudo tee --append /etc/environment > /dev/null
echo 'export LC_CTYPE="en_US.UTF-8"' | sudo tee --append /etc/environment > /dev/null
```

* After setting up the Environment, close the secure shell session and start a new one and
```sh
echo $SERVER_NAME
```

* This should output your Ephemeral IP Address otherwise you should setup SERVER_NAME Variable again.

* After this process, Run these bunch of commands to intialize Docker Installation
```sh
sudo apt update
sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
```

* This Command is OS specific, Update the sources list w.r.t. your Base Instance image from Compute engine.
```sh
echo "deb https://apt.dockerproject.org/repo ubuntu-xenial main" | sudo tee /etc/apt/sources.list.d/docker.list
```

* After that we setup Docker
```sh
sudo apt-get update
apt-cache policy docker-engine
sudo apt-get install -y docker-engine
sudo systemctl status docker
```

* If the Status comes up somewhat like this, then Docker is running.
```
● docker.service - Docker Application Container Engine
   Loaded: loaded (/lib/systemd/system/docker.service; enabled; vendor preset: enabled)
   Active: active (running) since Mon 2016-10-03 10:21:37 UTC; 17s ago
     Docs: https://docs.docker.com
 Main PID: 5731 (dockerd)
   CGroup: /system.slice/docker.service
           ├─5731 /usr/bin/dockerd -H fd://
           └─5736 docker-containerd -l unix:///var/run/docker/libcontainerd/docker-containerd.sock --shim docker-containerd-shim --metrics-interval=0 --start-timeout 2m --state-d

Oct 03 10:21:36 orga-server dockerd[5731]: time="2016-10-03T10:21:36.822959549Z" level=info msg="Graph migration to content-addressability took 0.00 seconds"
Oct 03 10:21:36 orga-server dockerd[5731]: time="2016-10-03T10:21:36.823546418Z" level=warning msg="Your kernel does not support swap memory limit."
Oct 03 10:21:36 orga-server dockerd[5731]: time="2016-10-03T10:21:36.824082989Z" level=info msg="Loading containers: start."
Oct 03 10:21:36 orga-server dockerd[5731]: time="2016-10-03T10:21:36.864024348Z" level=info msg="Firewalld running: false"
Oct 03 10:21:36 orga-server dockerd[5731]: time="2016-10-03T10:21:36.955575597Z" level=info msg="Default bridge (docker0) is assigned with an IP address 172.17.0.0/16. Daemon opt
Oct 03 10:21:37 orga-server dockerd[5731]: time="2016-10-03T10:21:37.005024331Z" level=info msg="Loading containers: done."
Oct 03 10:21:37 orga-server dockerd[5731]: time="2016-10-03T10:21:37.005414449Z" level=info msg="Daemon has completed initialization"
Oct 03 10:21:37 orga-server dockerd[5731]: time="2016-10-03T10:21:37.005596206Z" level=info msg="Docker daemon" commit=23cf638 graphdriver=devicemapper version=1.12.1
Oct 03 10:21:37 orga-server systemd[1]: Started Docker Application Container Engine.
Oct 03 10:21:37 orga-server dockerd[5731]: time="2016-10-03T10:21:37.013683025Z" level=info msg="API listen on /var/run/docker.sock"
lines 1-19/19 (END)
```

* For the Next Step we'll setup Docker Compose.
```sh
sudo apt-get -y install python3-pip
sudo pip install docker-compose
```


## Final Phase

* Now that Docker Compose is setup in our Instance, we'll execute:
```sh
git clone https://github.com/fossasia/open-event-server.git && cd open-event-server
sudo docker-compose build
sudo docker-compose up
```

* Once your Docker container is up, you need to configure the db container 'postgres for your app', Leaving that running as is, open another secure shell to your instance and run
```sh
sudo docker-compose run postgres psql -h postgres -p 5432 -U postgres --password
# Enter 'test' as password
```

* then,
```
postgres=# create database opev;
# CREATE DATABASE
postgres=# \q
# EXIT pg shell
```

* Once you are done with that,
```sh
sudo docker-compose run web /bin/bash
```

* Once you are running bash in your container as root,
```sh
python3 create_db.py
# The Email & Password entered here would be your Admin Email
python3 manage.py db stamp head
```

* Now that db is setup, you can kill both the running containers by ^C, and then run
```sh
sudo docker-compose up -d
```


#### After that, finally your own instance of orga-server would be running at your Ephemeral IP address.
<br><br>
#### Some Issues you might run into:
* pip 8.1.1 is not stable, so you might get [Upgrading solves this issue]:
```
Exception:
Traceback (most recent call last):
  File "/usr/lib/python3.5/dist-packages/pip/basecommand.py", line 209, in main
    status = self.run(options, args)
  File "/usr/lib/python3.5/dist-packages/pip/commands/install.py", line 317, in run
    requirement_set.prepare_files(finder)
  File "/usr/lib/python3.5/dist-packages/pip/req/req_set.py", line 360, in prepare_files
    ignore_dependencies=self.ignore_dependencies))
  File "/usr/lib/python3.5/dist-packages/pip/req/req_set.py", line 448, in _prepare_file
    req_to_install, finder)
  File "/usr/lib/python3.5/dist-packages/pip/req/req_set.py", line 387, in _check_skip_installed
    req_to_install.check_if_exists()
  File "/usr/lib/python3.5/dist-packages/pip/req/req_install.py", line 1011, in check_if_exists
    self.req.project_name
AttributeError: 'Requirement' object has no attribute 'project_name'
```
