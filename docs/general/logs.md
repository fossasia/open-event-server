# Logging


Certain information is being logged and stored in the database for future reference, resolving conflicts in case of hacks and for maintaining an overview of the system.
These are -

1. Create/Update/Delete Event
2. Create/Update User
3. Update user email
4. Assign/Edit/Remove an event-level role
5. Create/Update/Delete Track
6. Send Invite for Event
7. Assign/Remove a system level role
8. Publish/Unpublish event
9. Import/Export Event
10. Add Speaker to Session
11. Create/Update/Delete Speaker
12. Create/Update/Delete Session
13. Login/Logout from user (tracking IP, browser, platform)


## How to log information

From the `app.helpers.data` module, import `record_activity` .
Then call it using the identifier of the activity-type and the parameters.
The list of identifiers is located in `app.models.activity`. At the time of writing, it looks like -

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
