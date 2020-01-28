# Roles

The system has two kind of role types: System Roles and Event Roles.

1. System roles are related to the Open Event organization and operators of the application.
2. Event Roles are related to the users of the system with their different permissions for events.

## 1. System Roles

There are three System Roles:

* Super Admin
* Admin
* Sales Admin

### 1.1 Access to User Features for Super Admin

The Super Admin can access all user features.

| Function | Role | View | Create, Edit, Assign, Unassign | Delete | BaseURLs |
| --- | --- | --- | --- | --- | --- |
| MANAGE OWN PROFILE | Super Admin | YES | YES | YES | /profile |
| MANAGE OWN EVENTS | Super Admin | YES | YES | YES | /create, /events, /events/ID |
| IMPORT/EXPORT OWN EVENTS | Super Admin | YES | YES | YES| |
| MANAGE OWN SESSIONS | Super Admin | YES | YES | YES| |
| MANAGE SESSIONS OF OWN EVENTS | Super Admin | YES | YES | YES | |

### 1.2 Access to Admin Panels

The Super Admin and Admin can access all admin panels.

| Function | Role | View | Create, Edit, Assign, Unassign | Delete | BaseURLs |
| --- | --- | --- | --- | --- | --- |
| ALL ROLES PERMISSIONS | Super Admin / Admin | YES | YES |  YES | /admin/permissions |
| EVENTS AND SCHEDULES | Super Admin | YES | YES |  YES | |
| ADMINISTRATION | Super Admin / Admin | YES | YES |  YES | /admin/* |
| ALL EVENTS | Super Admin / Admin | YES | YES |  YES | /admin/events/|
| IMPORT/EXPORT OF ALL EVENTS / Admin | Super Admin | YES | YES |  YES | /admin/events/ |
| ALL SESSIONS | Super Admin / Admin | YES | YES |  YES | /admin/sessions/ |
| ALL USERS | Super Admin / Admin | YES | YES |  YES | /admin/users/ |
| ALL REPORTS | Super Admin / Admin | YES | YES |  YES | /admin/reports |
| ALL SALES | Super Admin / Admin | YES | YES |  YES | /admin/sales |
| ALL MESSAGES | Super Admin / Admin | YES | YES |  YES | /admin/messages |
| ALL SETTINGS | Super Admin / Admin | YES | YES |  YES | /admin/settings |
| ALL MODULES | Super Admin / Admin | YES | YES |  YES | /admin/modules |
| ALL Content | Super Admin / Admin | YES | YES |  YES | /admin/content |

The Sales Admin can only access the Sales Panel.

| Function | Role | View | Create, Edit, Assign, Unassign | Delete | BaseURLs |
| --- | --- | --- | --- | --- | --- |
| ALL SALES | Sales Admin | YES | YES |  YES | /admin/sales


## 2. Event Roles

### 2.1 Organizer

Organizer can access:
 - HOME
 - PROFILE(only his)
 - CREATE EVENT
 - MANAGE EVENTS(Can view all events but edit/remove only assigned events)
 - SPECIFIC EVENT DASHBOARD(View any events dashboard but only edit assigned events)
 - EDIT EVENT DETAILS(only assigned events)
 - EDIT EVENT SPEAKERS(assigned events only)
 - EDIT EVENT SPONSORS(assigned events only)
 - SCHEDULE TRACKS,ROOMS,TIMES OF EVENTS(edit and add tracks)
 - ASSIGN EVENT ROLES(only for his/her assigned event)
 - SPEAKER/ORGANIZER CREATES NEW SESSIONS
 - PROPOSALS AND SESSIONS FOR ADMINS(edit sessions for assigned events)
 - PROPOSALS AND SESSIONS FOR SPEAKERS(view sessions and proposals for speakers of assigned events only)
 - SEE EVENT AND SCHEDULE

3. Co-organizer can access:
 - HOME
 - PROFILE(only his)
 - CREATE EVENT
 - MANAGE EVENTS(Can view all events but edit only assigned events)
 - SPECIFIC EVENT DASHBOARD(View any events dashboard but only edit assigned events)
 - EDIT EVENT DETAILS(only assigned events)
 - EDIT EVENT SPEAKERS(assigned events only)
 - EDIT EVENT SPONSORS(assigned events only)
 - SCHEDULE TRACKS,ROOMS,TIMES OF EVENTS(add and edit tracks)
 - SPEAKER/ORGANIZER CREATES NEW SESSIONS
 - PROPOSALS AND SESSIONS FOR ADMINS(edit sessions for assigned events)
 - PROPOSALS AND SESSIONS FOR SPEAKERS(view sessions and proposals for speakers of assigned events only)
 - SEE EVENT AND SCHEDULE

4. Track-organizer can access:
 - HOME
 - PROFILE(access only his)
 - CREATE EVENT
 - MANAGE EVENTS(Can only view all events)
 - SPECIFIC EVENT DASHBOARD(View any events dashboard)
 - SCHEDULE TRACKS,ROOMS,TIMES OF EVENTS(drag and drop tracks for assigned events)
 - SEE EVENT AND SCHEDULE

5. Moderator can access:
 - HOME
 - PROFILE(only his)
 - CREATE EVENT
 - MANAGE EVENTS(Can only view events)
 - SPECIFIC EVENT DASHBOARD(View any events dashboard)
 - EDIT EVENT SPEAKERS(only view event's speakers, not edit them)
 - PROPOSALS AND SESSIONS FOR ADMINS(only view sessions for events)
 - PROPOSALS AND SESSIONS FOR SPEAKERS(view sessions and proposals for speakers of assigned events only)
 - SEE EVENT AND SCHEDULE

6. Speaker can access:
 - HOME
 - PROFILE(only his)
 - CREATE EVENT
 - MANAGE EVENTS(only view events)
 - SPECIFIC EVENT DASHBOARD(only view details of particular event)
 - SPEAKER/ORGANIZER CREATES NEW SESSIONS(create new sessions for an event)
 - PROPOSALS AND SESSIONS FOR SPEAKERS(view sessions and proposals for speakers of assigned events only)
 - SEE EVENT AND SCHEDULE

7. Anonymous user can access:
 - HOME(Can create event, view upcoming events and call for speakers)
 - PROFILE(Own profile)
 - CREATE EVENT
 - MANAGE EVENTS(only view list of all events)
 - SPECIFIC EVENT DASHBOARD(only view details regarding specific event)
 - SEE EVENT AND SCHEDULE


## Using Permissions system

After running `create_db.py` Event-specific-Roles, Services and Permissions are created.

### Event Specific Roles

```
organizer
coorganizer
track_organizer
moderator
speaker
```

The Organizer is the creator of the event and can access anything related to the event (Track, Session, Speaker, Sponsor, Microlocation).

Co-organizer, just like Organizer can access anything but cannot manage user roles.

Track Organizer can only Update and Read Tracks for that event.

Moderator can only Read Tracks before they are published but cannot edit them.

Speaker can read his own sessions (even unpublished), and can edit his own information.

### Site Specific Roles (Staff)

```
admin
super_admin
```

They have access to all the resources. There can be multiple Admins but just one Super Admin. Only the Super Admin can assign users as Admins.

You can check if a user is an Admin or Super Admin using:

```python
user.is_admin
user.is_super_admin
```

You can directly check if a user comes under Staff (Admin or Super Admin):

```python
user.is_staff
```


### Services

Services come under an event. We define the following as services:

```
track
session
speaker
sponsor
microlocation
```

To check if a user is a speaker in a session use:

```python
user.is_speaker_at_session(session_id)
```


## Example code

```
>>> from app.models.permission import Permission
>>> for p in Permission.query.all():
...  create = 'Create' if p.can_create else ''
...  read = 'Read' if p.can_read else ''
...  update = 'Update' if p.can_update else ''
...  delete = 'Delete' if p.can_delete else ''
...  print p.role, p.service, create, read, update, delete
...
<Role u'organizer'> <Service u'track'> Create Read Update Delete
<Role u'organizer'> <Service u'session'> Create Read Update Delete
<Role u'organizer'> <Service u'speaker'> Create Read Update Delete
<Role u'organizer'> <Service u'sponsor'> Create Read Update Delete
<Role u'organizer'> <Service u'microlocation'> Create Read Update Delete
#
<Role u'coorganizer'> <Service u'track'>  Read Update
<Role u'coorganizer'> <Service u'session'>  Read Update
<Role u'coorganizer'> <Service u'speaker'>  Read Update
<Role u'coorganizer'> <Service u'sponsor'>  Read Update
<Role u'coorganizer'> <Service u'microlocation'>  Read Update
#
<Role u'track_organizer'> <Service u'track'>  Read Update
#
<Role u'moderator'> <Service u'track'>  Read
```

The permissions printed above adhere to https://github.com/fossasia/open-event-server/issues/623

`User` class has the following methods to check its role:

```python
user.is_organizer(event_id)
user.is_coorganizer(event_id)
user.is_track_organizer(event_id)
user.is_moderator(event_id)
```


`User` class has the following methods to check permissions:

```python
user.can_create(service, event_id)
user.can_read(service, event_id)
user.can_update(service, event_id)
user.can_delete(service, event_id)
```

e.g.
```
>>> from app.models.user import User
>>> from app.models.track import Track
>>> u = User.query.all()[0]
>>> u.can_create(Track, event_id=1)
True
>>> u.can_update(Track, event_id=1)
True
>>> u.can_update(Track, event_id=2)
False
```

You can define a user's role for an event in `UsersEventsRoles`.


Here's an example showing how a user is assigned as a Track Organizer for an Event (with `event_id = 1`).

```
>>> from app.models.users_events_roles import UsersEventsRoles as UER
>>> from app.models.user import User
>>> from app.models.event import Event
>>> from app.models.role import Role
>>> r = Role.query.filter_by(name='track_organizer').first()
>>> e = Event.query.get(1)
>>> from app.helpers.data import save_to_db
>>> u = User(email='asd@email.com')
>>> save_to_db(u, 'asfd')
True
>>> uer = UER(user=u, event=e, role=r)
>>> save_to_db(uer, 'asdf')
True
>>> from app.models.session import Session
>>> from app.models.track import Track
# 'u' is a track organizer and can only update and read tracks for an event.
>>> u.can_create(Track, 1)
False
>>> u.can_read(Track, 1)
True
>>> u.can_update(Track, 1)
True
>>> u.can_delete(Track, 1)
False
```
