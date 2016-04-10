# How to deploy server to Heroku

Here are the steps:

* We need to install heroku on our machine.Type the following in your linux terminal:
	* ```wget -O- https://toolbelt.heroku.com/install-ubuntu.sh | sh```
  This installs the Heroku Toolbelt on your machine to access heroku from the command line.
* Next we need to login to our heroku server(assuming that you have already created an account).Type the following in the terminal:
	* ```heroku login```
  You will see the following output:
	Enter your Heroku credentials.
	Email: gamesbrainiac@gmail.com
	Password (typing will be hidden):
	Logged in as gamesbrainiac@gmail.com
* Once logged in we need to create a space on the heroku server for our application.This is done with the following command
	* ```heroku create```
* We need to initialize our git repository and push the master branch of our repository to heroku.Type:
	* ```git init```
  If the commit isn't changed to master we need to do so by typing the following commands on terminal:
	* ```git add -A```
	* ```git commit -m "Initial Commit."```
	* ```git push origin master```
* Next we create our requirements.txt file using the pip command:
	* ```pip freeze > requirements.txt```
* The next step is creating a Procfile. This can be done by using a production ready web server called gunicorn.The contents of   the Procfile will be:
	* ```web: gunicorn <app>:app```
  Here, the <app> will be replaced by the name of the application without the .py at its end.Basically a Procfile tells heroku   what to name our process which runs our   web application.
* Before deploying to heroku, make sure that the app works locally on the designated port.
* Finally we deploy the code to heroku.Its very simple, just type:
	* ```git push heroku master```
  At the end of the process a URL will be generated where our flask application will run.
