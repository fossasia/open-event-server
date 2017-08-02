# Import/Export


Import/Export feature of Open Event allows you to export an event with all its data in a zip file.
You can then use the zip to import back the event on an another system.

### The zip structure

Zip structure is as follows -

```sh
- images\
-   sponsors\
-   speakers\
-   logo.ext
- videos\
- audios\
- slides\
- event
- meta
- speakers
- sponsors
- sessions
- tracks
# and more data files
```

### The data files

Files at the root of the zip are text files and contain the event information. These are -

```sh
event
meta
forms
microlocations
sessions
session_types
speakers
sponsors
tracks
```

The data they store corresponds to the GET APIs and has the same format as them. Here is the complete list -

* `event` - /api/v1/events/{event_id}
* `microlocations` - /api/v1/events/{event_id}/microlocations
* `sessions` - /api/v1/events/{event_id}/sessions
* `session_types` - /api/v1/events/{event_id}/sessions/types
* `speakers` - /api/v1/events/{event_id}/speakers
* `sponsors` - /api/v1/events/{event_id}/sponsors
* `tracks` - /api/v1/events/{event_id}/tracks

The files which are not related to APIs are described as follows -

* `meta` - Extra information about the export. It has the following fields -
    * `root_url` - base url of the server from which event was exported

* `forms` - Sessions and Speaker form data for an event i.e. it stores information about which fields are required and which are optional in the Session and Speaker form.


### The binaries/media

Media files of the event are stored inside the images, audios, videos and slides folder respectively depending on their type.
The following is the directory structure of the media files in the zip.
For example, videos of sessions will have a location in zip like `/videos/session_ID` where session_ID is the id of the session.
The filename might be followed by an extension. Example - /videos/session_4.mp4

```json
{
    'sessions': {
        'video': '/videos/session_ID',
        'audio': '/audios/session_ID',
        'slides': '/slides/session_ID'
    },
    'speakers': {
        'photo': '/images/speakers/photo_ID'
    },
    'event': {
        'logo': '/images/logo',
        'background_image': '/images/background'
    },
    'sponsors': {
        'logo': '/images/sponsors/logo_ID'
    },
    'tracks': {
        'track_image_url': '/images/tracks/image_ID'
    }
}
```
