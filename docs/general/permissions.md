# Permission manager

## **What is permission manager?**
Simply checking for the permission for each method. Instead of making decorators work on different views. The use of permission manager is based on the concept that "First prepare the things that permission decorator require to test the validation and then pass it to permission decorator"

### **How it is implemented?**

1. Separating the ```api``` initialization  to `app\api\bootstrap.py` so that it can be used in routes files  (like events.py, users.py, etc)
2. In this basic implementation, please see `tickets.py`.
3. As an example use, a decorator added to tickets.py as`api.has_permission('is_organizer', fetch='event_id', model=Ticket),`
4. Created a permission manager `app\api\helpers\permission_manager.py` which will do the whole work.


### **Using Permission Manager**

Permission Manager receives five parameters as:
`def permission_manager(view, view_args, view_kwargs, *args, **kwargs):`

First three are provided into it implicitly by flask-rest-jsonapi module

- view: This is the resource’s view method which is called through the API. For example if I go to /events then the get method of ResourceList will be called.
- view_args: These are args associated with that view
- view_kwargs: These are kwargs associated with that resource view. It includes all your URL parameters as well
- args: These are the custom args which are provided when calling the permission manager. Here at permission manager is it expected that the first index of args will be the name of permission to check for.
- kwargs: This is the custom dict which is provided on calling the permission manager. The main pillar of the permission manager. Described below in usage


Using permission manager is basically understanding the different options you can send through the kwargs so here is the list of the things you can send to permission manager

*These are all described in the order of priority in permission manager*

- **method (string)**: You can provide a string containing the methods where permission needs to be checked as comma separated values of different methods in a string.
For example: method=”GET,POST”
- **leave_if (lambda)**: This receives a lambda function which should return boolean values. Based on returned value if is true then it will skip the permission check. The provided lambda function receives only parameter, “view_kwargs”
Example use case can be the situation where you can leave the permission for any specific related endpoint to some resource and would like to do a manual check in the method itself.
- **check (lambda)**: Opposite to leave_if. It receives a lambda function that will return boolean values. Based on returned value, If it is true then only it will go further and check the request for permissions else will throw forbidden error.
- **fetch (string)**: This is the string containing the name of the key which has to be fetched for fetch_as key (described below). Permission manager will first look for this value in view_kwargs dict object. If it is not there then it will make the query to get one(described below at model )
- **fetch_as (string)**: This is the string containing the name of a key. The value of fetch key will be sent to the permission functions by this name. If fetch_as is same as fetch, there is no need to set fetch_as
- **model (string)**: This is one most interesting concept here. To get the value of fetch key. Permission manager first looks into view_kwargs and if there no such value then you can still get one through the model. The model attribute here receives the class of the database model which will be used to get the value of fetch key.
It makes the query to get the single resource from this model and look for the value of fetch key and then pass it to the permission functions/methods.
The interesting part is that by default it uses < id> from view_kwargs to get the resource from the model but in any case if there is no specific ID with name < id> on the view_kwargs. You can use these two options as:

	- **fetch_key_url (string)**: This is the name of the key whose value will be fetched from view_kwargs and will be used to match through the records in database model to get the resource.
	-** fetch_key_model (string)**: This is the name of the match column in the database model for the fetch_key_url, The value of it will be matched with column named as the value of fetch_key_model.

**In case there is no record found in the model then permission manager will throw NotFound 404 Error.**

### Multiple Fetch Mode
Permission manager support multiple fetch mode where a particular value can be fetched from more than one database model.
#### To use multiple mode
Instead of providing single model to **model** option of permission manager, provide an array of models. Also there is option to provide to provide comma separated values to **fetch_key_url**
Now there can be scenario where you want to fetch resource from database model using different keys present on your **view_kwargs**
for example, consider these endpoints
`/notifications/<notification_id>/event`
`/orders/<order_id>/event`
Since they point to same resource and if you want to ensure that logged in user is organizer then you can use these two things as:
**fetch_key_url=**"notification_id, order_id"
**model=**[Notification, Order]
Permission manager will always match indexes in both options i.e, first key of fetch_key_url will be only used for first key of model and so on.
**fetch_key_url** is an optional parameter and even in multiple mode you can provide single value as well.  But if you provide multiple comma separated values make sure you provide all values i.e, no of values in **fetch_key_url** and **model** must be equal.
Now **fetch** also accepts comma separated string. **Please note that the values in fetch string are checked as logical OR so if anyone gets the match then it stops there and use it.**

DOCS: http://flask-rest-jsonapi.readthedocs.io/en/latest/permission.html
