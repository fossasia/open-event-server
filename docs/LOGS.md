# Logging

Certain information is being logged and stored in the database for future reference, resolving conflicts in case of hacks and for maintaining an overview of the system.
These are -

1. Create Event
2. Update Event
3. Delete Event
4. Create User
5. Update User
6. Assign an event-level role
7. Edit an event-level role
8. Remove an event-level role
9. Create Session


## How to log information

From the `open_event.helpers.data` module, import `record_activity` .
Then call it using the identifier of the activity-type and the parameters.
The list of identifiers is located in `open_event.models.activity`. At the time of writing, it looks like -

```python
ACTIVITIES = {
    'create_user': 'User {user} created',
    'update_user': 'Profile of user {user} updated',
    'update_event': 'Event {event_id} updated',
    'create_event': 'Event {event_id} created',
    'delete_event': 'Event {event_id} deleted',
    'create_role': 'Role {role} created for user {user} in event {event_id}',
    'update_role': 'Role updated to {role} for user {user} in event {event_id}',
    'delete_role': 'User {user} removed from role {role} in event {event_id}',
    'create_session': 'Session {session} was created in event {event_id}'
}
```

Now, if for example you want to record a delete event activity, you call

```python
record_activity('delete_event', event_id=event_id)
```
