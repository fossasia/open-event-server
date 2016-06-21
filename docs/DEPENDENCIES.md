## Authentication OAuth ##
Responsible Person: Aditya Vyas
We are using it to get information from Facebook and Google account, and we allow to user sign in.
 1. Google https://accounts.google.com/o/oauth2/auth
 2. Facebook https://graph.facebook.com/oauth

## Location ##
We are based on Google maps to get information about location(info about country, city, latitude and longitude)https://maps.googleapis.com/maps/api/
We use it to get current location and display closes events.

## Amazon S3 ##
Responsible Person: Avi Aryan
We use it to storage audio, avatars and logos
You can see whole documentation how it works [in our documentation](https://github.com/fossasia/open-event-orga-server/blob/development/docs/AMAZON_S3.md#amazon-s3)

## Sending Emails ##
To send emails we are using sendgrid
https://api.sendgrid.com/api/mail.send.json

## Getting information about current version ##
Responsible Person: Rafal Kowalski, Niranjan Rajendran
We use heroku releases to see which version is deployed https://api.heroku.com/apps/open-event/releases
and we also use Github to get info about commit(for example: commit message, author name) ahttps://api.github.com/repos/fossasia/open-event-orga-server/commits

## Env Variables Heroku ##
Responsible Person: Rafal Kowalski
To see our all enviroment variables you have to visit Heroku page
https://dashboard-classic.heroku.com/apps/open-event/settings (You need access to see this page)
