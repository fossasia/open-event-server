## **What is permission manager?**
Simply checking for the permission for each method. Instead of making decorators work on different views. The use of permission manager is based on the concept that "First prepare the things that permission decorator require to test the validation and then pass it to permission decorator"

### **How it is implemented?**

1. Separating the ```api``` intialization  to `app\api\bootstrap.py` so that it can be used in routes files  (like events.py, users.py, etc)
2. In this basic implementation, please see `tickets.py`.
3. As an example use, a decorator added to tickets.py as`api.has_permission('is_organizer', fetch='event_id', fetch_as="event_id", model=Ticket),`
4. Created a permission manager `app\api\helpers\permission_manager.py` which will do the whole work.

### **How it works?**
Let's look into `is_organizer` decorator. We know that it requires `event_id` to check if the user is associated as the organizer of that event or not.

Now if we call `/tickets/<int:id>` We do not have ```event_id``` which is required by `is_organizer`, Here we are using 
`api.has_permission('is_organizer', fetch='event_id', fetch_as="event_id", model=Ticket) `

_first arg_ => Name of the permission to use
_fetch_as_ => Name of key need to send to the decorator
_fetch_ => Name of the column in the model where we will find the value of the fetch_as key name
_model_ => Model to use to fetch the key value

There are two optional parameters
`methods` => Comma separated string telling which methods are applicable for this check (default = GET,POST,DELETE,PATCH)

`fetch_key_url` (default=`id`) => This is the name of URL parameter whose value will be used to find the record from database.

`fetch_key_model` => This is the name of coulmn in the database model with which the `fetch_key_url` will be matched.


DOCS: http://flask-rest-jsonapi.readthedocs.io/en/latest/permission.html