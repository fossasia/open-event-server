# Digital Ocean

This guide will show you how to deploy Open Event on Digital Ocean. The basic idea is installing Docker on Digital Ocean droplet and then running Open Event in it.

#### Phase 1

* Create a droplet with Ubuntu x64 as the image. At the time of writing this guide, Ubuntu 16.04.1 was used.

* Choose a size with **atleast 1 GB RAM**. We found 512 MB RAM to be insufficient when running Open Event inside Docker.

* Choose other options according to need and then 'Create' the droplet.

* Once droplet has been created, you will get email from DigitalOcean with its information IP Address, username and password.

![droplet_email](https://cloud.githubusercontent.com/assets/4047597/17770515/e2ea6f4c-655b-11e6-9211-78257a083e82.png)

* Open a terminal window and ssh into the server. The command is `ssh USERNAME@IP`. When run, it will ask for the password you got through email. Ctrl-Shift-V to paste the password and ENTER. An example has been given below.

```bash
ssh root@104.236.228.132
# Enter password you got in the email and enter
```

* If you are ssh'ing into your droplet for the first time, you will get a prompt to change password. The step is compulsory so change the password here.
Once this step is done, you will be running the droplet's shell.


#### Phase 2

The steps that will be mentioned now are analogous to [running Open Event on Docker](docker.md) documentation. You are recommended to first go through it to appreciate the
similarities.

* Now as we have just initialized our brand new server, the first step is to install Docker. DigitalOcean has a
[nice guide](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04) on installing Docker in Ubuntu 16.04 so follow it.
I took the commands from that guide and have written them here. You can copy paste the following into the droplet's ssh shell.

```bash
sudo apt-get update
sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
echo "deb https://apt.dockerproject.org/repo ubuntu-xenial main" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-get update
apt-cache policy docker-engine
sudo apt-get install -y docker-engine
sudo systemctl status docker
```

* Next step is to install Docker-Compose. Following the [DigitalOcean guide](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-14-04), run the following commands in the ssh shell to install compose.

```bash
sudo apt-get -y install python3-pip
sudo pip install docker-compose
```

* Now that Docker and Compose are setup, it's time to build the image. The next steps are very similar to the [running Open Event on Docker](docker.md)
tutorial so please see it.

* We will start by cloning the GitHub Open Event Orga Server repo and cd'ing into it's directory. Then we will set the `SERVER_NAME` and then build and run the image.

```bash
git clone https://github.com/fossasia/open-event-server.git && cd open-event-server
export SERVER_NAME=104.236.228.132
docker-compose build
docker-compose up
```

* The above commands will have the server running but we still have to create the database. So open a new terminal window in your local system (Ctrl-Alt-T) and then
ssh into the droplet.

```bash
ssh USERNAME@IP
# Example - ssh root@104.236.228.132
# Enter the new password you set and Enter
```

* In the new ssh window, run the following command -

```bash
docker-compose run postgres psql -h postgres -p 5432 -U postgres --password
# Enter password as test
```

* When PSQL opens, create the database and then quit using `\q`.

```sql
create database opev;
# CREATE DATABASE
```

* Now we have to create the tables. In the same (2nd) terminal window, run -

```bash
docker-compose run web /bin/bash
```

* When bash opens, run the following commands and exit.

```bash
python3 create_db.py
# ^^ write super_admin email and password when asked
python3 manage.py db stamp head
```

* That's it. Visit the `$IP` (example 104.236.228.132) to view the open event server. You can close the 2nd terminal window if you wish.



### NOTES

* For demonstration purposes, I ran the server in normal mode. ( `docker-compose up` )
The server will die as soon as the first terminal window is closed. To not let that happen, start the the server as daemon.

```bash
docker-compose up -d
```

* If you haven't added a domain name to your DO droplet and are accessing it through the IP, you might face the problem of not being able to login. This is a Chrome issue
and may exist in other browsers too (haven't tested). Learn more about it in this [Stack Overflow answer](http://stackoverflow.com/a/27276450/2295672). The only way to solve
this is by attaching a domain name to your droplet.

* `SERVER_NAME` should be the same as the domain on which the project is running. Don't include http, https, www etc in server name.
Also don't include the trailing '/' in the domain name.
