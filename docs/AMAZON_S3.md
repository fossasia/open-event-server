## Amazon S3

### What is S3 ? Basic concepts

S3 is Amazon's platform for data storage. The main idea of S3 is based on buckets and keys.
Buckets are containers which store data. You create one bucket for one project.
Keys are the unique ID for an object inside the bucket (container).

If the bucket's name is 'abc' and key is 'def', then the full url for the object will be http://abc.s3.amazonaws.com/def .
It is interesting to note that key can include slashes. So if a key is 'image/2/full.png', then the full url will be http://abc.s3.amazonaws.com/image/2/full.png
This makes S3 easy and flexible for data storage.


### Setting up S3 for orga-server

1. Create account on AWS (https://aws.amazon.com/) . They will verify you with all sorts of methods so make sure you don't mess up.
2. Once account is created, sign in to [AWS Management Console](https://console.aws.amazon.com/console/home)
3. [Open S3](https://console.aws.amazon.com/s3/home) from the massive list of web services Amazon provides.
4. Click on the create bucket button to create a bucket. When the dialog opens, just enter a unique name and click "Create".
5. Bucket will be created and shown in the all bucket list.
6. Now it's time to create access tokens for your bucket. Choose "Security Credentials" option from the dropdown menu with your full name as label.
7. Choose IAM when the following dialog appears.
8. You will be presented with the [IAM Management Console](https://console.aws.amazon.com/iam/home). Click on "Create New Users".
9. Enter a username (example `opev_user`) and click on "Create".
10. You will be shown the user credentials. Don't download them. **Copy them and keep them safe**. Then click on "Close".
11. You will be at IAM Users list now.
12. Now that the user has been created, it's time to give it bucket permissions.
    Click on [Policies](https://console.aws.amazon.com/iam/home?region=us-west-2#policies) in the sidebar.
13. Click on "Create Policy" button and choose "Create your own Policy".
14. Enter a policy name, a description and the following in the policy document. (Be sure to **replace 'opevbucketname' with your bucket name.**)

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
        }
    ]
}
```

15. Once policy is created, go back to [Users](https://console.aws.amazon.com/iam/home#users) tab from the sidebar.
16. Click on `opev_user` (the user you just created) and when the user loads, open "Permissions" tab.
17. Click on "Attach policy" button, search for the policy you just created (here opev\_bucket\_access) and attach it.
18. You will be redirected back to user permissions tab but now it will have that policy.
19. That's it. Set the environment variables `BUCKET_NAME`, `AWS_KEY` and `AWS_SECRET` to their respective values and the server will use S3 for storage.
20. Here `BUCKET_NAME` is 'opevbucketname' and `AWS_KEY` and `AWS_SECRET` are what you got from step 10.


#### References

* [Intro to S3](http://docs.aws.amazon.com/AmazonS3/latest/gsg/GetStartedWithS3.html)
* [Developer guide](http://docs.aws.amazon.com/AmazonS3/latest/dev/Welcome.html)
* [S3 Permissions](http://docs.aws.amazon.com/AmazonS3/latest/dev/using-with-s3-actions.html)
* [Direct to S3 Uploading](https://devcenter.heroku.com/articles/s3-upload-python)
