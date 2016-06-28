We use [Bower](http://bower.io) to manage front-end dependencies. `cd` to the directory where `bower.json` is stored and run:
* First we have to install npm and nodejs. Run the following:
```sudo apt-get install npm```

* Then run the following command to get Bower:
```sudo npm install -g bower```

* Finally run the following command to install the dependencies from bower.json:
```
bower install
```

Note: If you are working from within a proxied network of an organization/institute, Bower might not be able to install the libraries. For that, we need to configure .bowerrc to work via proxy.
* Open .bowerrc in any text editor like vim. Run:
```vim .bowerrc```
* The contents of .bowerrc will be something like this:
```
{
	"directory": "open_event/static/admin/lib"
}
```
* Modify the file to add "proxy" and "https-proxy" properties like this:
```
{
	"directory": "open_event/static/admin/lib",
	"proxy": "http://172.31.1.23:8080",
	"https-proxy": "http://172.31.1.23:8080"
}
```
* Save and exit. Now we can run ```bower install``` to install our libraries.