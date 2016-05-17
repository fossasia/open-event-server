# How to deploy server to Heroku

### Steps

* We need to install heroku on our machine. Type the following in your linux terminal:
	* ```wget -O- https://toolbelt.heroku.com/install-ubuntu.sh | sh```
  This installs the Heroku Toolbelt on your machine to access heroku from the command line.
* Next we need to login to our heroku server(assuming that you have already created an account). Type the following in the terminal:
	* ```heroku login```
    * Enter your credentials and login.
* Once logged in we need to create a space on the heroku server for our application. This is done with the following command
	* ```heroku create```
* Now it's time to set the `DATABASE_URL` env var.
    * ```heroku config:set DATABASE_URL=postgresql://postgres:start@localhost/test```
* Once the app is created, we need to create a database for it.
    * ```heroku addons:create heroku-postgresql:hobby-dev```
    * ```heroku pg:promote <HEROKU_POSTGRESQL_COLOR_URL>```
* Then we deploy the code to heroku. Its very simple, just type:
	* ```git push heroku master```
    * ```git push heroku yourbranch:master``` if you are in a different branch than master
* Finally, time to create tables on the server. Also in case of model updates, run the following command -
    * ```heroku run migrate```
