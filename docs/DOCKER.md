## Install with Docker on Ubuntu:

* Get the latest version of docker. If you have problems with the install commands,
see the [official instructions](https://docs.docker.com/engine/installation/linux/ubuntulinux/) for your Ubuntu version.

```
sudo apt-get install linux-image-extra-`uname -r`
sudo apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
echo "deb https://apt.dockerproject.org/repo ubuntu-trusty main" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-get update
sudo apt-get install docker-engine
```

* Git clone the repository and cd into it.
 ```git clone https://github.com/fossasia/open-event-orga-server.git && cd open-event-orga-server```

* Build the app
 ```docker build -t open-event-orga-server .```

* Run the app
 ```docker run -p 80:5000 open-event-orga-server```
