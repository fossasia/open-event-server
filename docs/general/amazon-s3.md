# Amazon S3

## What is S3 ? Basic concepts

S3 is Amazon's platform for data storage. The main idea of S3 is based on buckets and keys.
Buckets are containers which store data. You create one bucket for one project.
Keys are the unique ID for an object inside the bucket (container).

If the bucket's name is 'abc' and key is 'def', then the full url for the object will be http://abc.s3.amazonaws.com/def .
It is interesting to note that key can include slashes. So if a key is 'image/2/full.png', then the full url will be http://abc.s3.amazonaws.com/image/2/full.png
This makes S3 easy and flexible for data storage.


## Setting up S3 for orga-server

1 - Create account on AWS (https://aws.amazon.com/).

2 - Once account is created, sign in to [AWS Management Console](https://console.aws.amazon.com/console/home)

3 - [Open S3](https://console.aws.amazon.com/s3/home) from the massive list of web services Amazon provides.

4 - Click on the create bucket button to create a bucket. When the dialog opens, just enter a unique name and click "Create".

![create_bucket](https://cloud.githubusercontent.com/assets/4047597/16184351/596ce8cc-36d9-11e6-9a20-f53b611fbcc2.png)

5 - Bucket will be created and shown in the all bucket list.

6 - Now it's time to create access tokens for your bucket. Choose "Security Credentials" option from the dropdown menu with your full name as label.

![sec_cred](https://cloud.githubusercontent.com/assets/4047597/16184350/5966a49e-36d9-11e6-831e-a40f51e1fe5a.png)

7 - Choose IAM when the following dialog appears.

![iam_box](https://cloud.githubusercontent.com/assets/4047597/16184349/5953359e-36d9-11e6-9501-e8a0f33ea1bc.png)

8 - You will be presented with the [IAM Management Console](https://console.aws.amazon.com/iam/home#users). Click on "Create New Users".

9 - Enter a username (example `opev_user`) and click on "Create".

![create_user](https://cloud.githubusercontent.com/assets/4047597/16184348/5949baf0-36d9-11e6-8c5c-6bf91fc97b8d.png)

10 - You will be shown the user credentials. Don't download them. **Copy them and keep them safe**. Then click on "Close".

![user_creds](https://cloud.githubusercontent.com/assets/4047597/16184342/58f5631a-36d9-11e6-839b-0e0502d60267.png)

11 - You will be at IAM Users list now.

![users_list](https://cloud.githubusercontent.com/assets/4047597/16184347/59434cce-36d9-11e6-890f-c88f3bd490f9.png)

12 - Now that the user has been created, it's time to give it bucket permissions. Click on [Policies](https://console.aws.amazon.com/iam/home?region=us-west-2#policies) in the sidebar.

13 - Click on "Create Policy" button and choose "Create your own Policy".

![create_own_policy](https://cloud.githubusercontent.com/assets/4047597/16184346/593d8a0a-36d9-11e6-9dea-247626c283de.png)

14 - Enter a policy name, a description and the following in the policy document. (Be sure to **replace 'opevbucketname' with your bucket name.**)

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetBucketLocation"
            ],
            "Resource": "arn:aws:s3:::opevbucketname"
        },
        {
            "Effect": "Allow",
            "Action": "*",
            "Resource": "arn:aws:s3:::opevbucketname/*"
        },
        {
            "Effect": "Allow",
            "Action": "s3:ListAllMyBuckets",
            "Resource": "arn:aws:s3:::*"
        }
    ]
}
```

![policy_docu](https://cloud.githubusercontent.com/assets/4047597/16184345/59089a20-36d9-11e6-8ac0-9b16155207cd.png)

15 - Once policy is created, go back to [Users](https://console.aws.amazon.com/iam/home#users) tab from the sidebar.

16 - Click on `opev_user` (the user you just created) and when the user loads, open "Permissions" tab.

![user_policy](https://cloud.githubusercontent.com/assets/4047597/16184344/59007c32-36d9-11e6-885e-9ea05cff0a30.png)

17 - Click on "Attach policy" button, search for the policy you just created (here opev\_bucket\_access) and attach it.

18 - You will be redirected back to user permissions tab but now it will have that policy.

![policy_done](https://cloud.githubusercontent.com/assets/4047597/16184343/58fa292c-36d9-11e6-9a0f-bf629c04922e.png)

19 - That's it. Set the environment variables `BUCKET_NAME`, `AWS_KEY` and `AWS_SECRET` to their respective values and the server will use S3 for storage.

20 - Here `BUCKET_NAME` is 'opevbucketname' and `AWS_KEY` and `AWS_SECRET` are what you got from step 10.



## Using the (S3) storage module in code

S3 works on the concept of keys. Using the same idea, `app.helpers.storage` module has been created to allow uploading files to both S3 and local server.
Here is a basic example.

```python
from flask import request, current_app as app
from app.helpers.storage import upload
import flask_login as login

@app.route('/users/upload/', methods=('POST'))
def view():
    profile_pic = request.files['profile_pic']
    url = upload(profile_pic, 'users/%d/profile_pic' % login.current_user.id)
    print url  # full URL to the uploaded resource, either on local server or S3
```

`upload` takes 2 parameters; the file object and the key. The key should be chosen wisely according to the purpose.
For example,
- When uploading user avatar, key should be 'users/{userId}/avatar'
- When uploading event logo, key should be 'events/{eventId}/logo'
- When uploading audio of session, key should be 'events/{eventId}/sessions/{sessionId}/audio'

This helps to avoid conflicts on the server and keep data distinct.

Another important feature of upload is that it automatically switches to uploading on local server if AWS env vars are not set. So it doesn't affect development
workflow. `upload` can be used in a uniform way without worrying where the data will be stored.

Also note that upload always returns the absolute link of the file that is uploaded. So you can use the returned url directly in templates i.e. no need to use
``{{ url_for('static', uploadedUrl) }}`, just use `{{uploadedUrl}}`.



## References

* [Intro to S3](http://docs.aws.amazon.com/AmazonS3/latest/gsg/GetStartedWithS3.html)
* [Developer guide](http://docs.aws.amazon.com/AmazonS3/latest/dev/Welcome.html)
* [S3 Permissions](http://docs.aws.amazon.com/AmazonS3/latest/dev/using-with-s3-actions.html)
* [Direct to S3 Uploading](https://devcenter.heroku.com/articles/s3-upload-python)
