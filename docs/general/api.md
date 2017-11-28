# API

All the APIs of development branch are right now hosted in `/v1/`.

## API Authentication

To get access token, send a POST request to `/auth/session` with email and password.

```json
{
  "email": "email@domain.com",
  "password": "string"
}
```

The return will be as follows in case of success.

```json
{
  "access_token": "some_random_string"
}
```

Then use the `access_token` in a request by setting the header `Authorization` to `JWT <access_token>`.


## Swagger Docs

Swagger API documentation with live-testing feature is available at `/api/v1` endpoint of the server where Open Event is hosted.
For the current dev deployement, it is at http://open-event-dev.herokuapp.com/api/v1/ and for the master deployement, it is at
http://open-event.herokuapp.com/api/v1/

Don't forget to login into the swagger UI (through the top right link) to get access to all authorized API methods (like POST, PUT).

**Note** - A static documentation with no live-testing feature is available at http://fossasia.github.io/open-event-server/api/v1/. In case the above documentation links
are down/dead, please refer to it. It will always contain docs of latest version of Open Event Orga Server.


## API Fields

Serialized headers are main models (e.g. `Event`, `Session`, etc.). Others  are nested fields (e.g. `SessionSpeaker`, `TrackSession`, etc.).

Datatype, requirement and access-level has been defined for every model. Nested fields inherit the access-level defined for them in the model.

### 1. Event

| Field | Datatype | Requirement | Access |
| --- | --- | --- | --- |
|**id** | integer | Required | Public |
|**name** | string | Required | Public |
|**description** | string | Optional | Public |
|**event_url** | string | Optional | Public |
|**color** | string | Optional | Public |
|**logo** | string | Optional | Public |
|**location_name** | string | Optional | Public |
|**searchable_location_name** | string | Optional | Public |
|**starts_at** | string | Required | Public |
|**ends_at** | string | Required | Public |
|**latitude** | number | Optional | Public |
|**longitude** | number | Optional | Public |
|**background_image** | string | Optional | Public |
|**state** | string | Optional | Public |
|**email** | string | Optional | Public |
|**organizer_name** | string | Optional | Public |
|**organizer_description** | string | Optional | Public |
|**type** | string | Optional | Public |
|**topic** | string | Optional | Public |
|**sub_topic** | string | Optional | Public |
|**ticket_url** | string | Optional | Public |
|**timezone** | string | Optional | Public |
|**privacy** | string | Optional | Public |
|**code_of_conduct** | string | Optional | Public |
|**schedule\_published\_on** | string | Optional | Public |
|**creator** | **EventCreator** | Required | Public |
|**copyright** | **EventCopyright** | Optional | Public |
|**social_links** | **EventSocial** | Optional | Public |
|**call_for_papers** | **EventCFS** | Optional | Public |
|**version** | **EventVersion** | Optional | Public |


#### EventCreator

| Field | Datatype | Requirement |
| --- | --- | --- |
|**id** | integer | Required |
|**email** | string | Required |

#### EventSocial

| Field | Datatype | Requirement |
| --- | --- | --- |
|**id** | integer | Required |
|**name** | string | Required |
|**link** | string | Required |

#### EventCopyright

| Field | Datatype | Requirement |
| --- | --- | --- |
|**holder** | string | Optional |
|**holder_url** | string | Optional |
|**licence** | string | Optional |
|**licence_url** | string | Optional |
|**logo** | string | Optional |
|**year** | integer | Optional |

#### EventCFS

| Field | Datatype | Requirement |
| --- | --- | --- |
|**announcement** | string | Optional |
|**end_date** | string | Optional |
|**privacy** | string | Optional |
|**start_date** | string | Optional |
|**timezone** | string | Optional |

#### EventVersion

| Field | Datatype | Requirement |
| --- | --- | --- |
|**event_ver** | integer | Required |
|**sessions_ver** | integer | Required |
|**speakers_ver** | integer | Required |
|**tracks_ver** | integer | Required |
|**sponsors_ver** | integer | Required |
|**microlocations_ver** | integer | Required |


### 2. Microlocation

| Field | Datatype | Requirement | Access |
| --- | --- | --- | --- |
|**id** | integer | Required | Public |
|**name** | string | Required | Public |
|**floor** | integer | Optional | Public |
|**latitude** | number | Optional | Public |
|**longitude** | number | Optional | Public |
|**room** | string | Optional | Public |


### 3. Session

Note: If the `microlocation` field of the session is null, the session is unscheduled in the event scheduler.

| Field | Datatype | Requirement | Access |
| --- | --- | --- | --- |
|**id** | integer | Required | Public |
|**title** | string | Required | Public |
|**subtitle** | string | Optional | Public |
|**short_abstract** | string | Optional | Public |
|**long_abstract** | string | Required | Public |
|**comments** | string | Optional | Public |
|**starts_at** | string | Required | Public |
|**ends_at** | string | Required | Public |
|**speakers** | Array[**SessionSpeaker**] | Optional | Public |
|**track** | **SessionTrack** | Optional | Public |
|**language** | string | Optional | Public |
|**microlocation** | **SessionMicrolocation** | Optional | Public |
|**session_type** | **SessionType** | Optional | Public |
|**video** | string | Optional | Public |
|**audio** | string | Optional | Public |
|**slides** | string | Optional | Public |
|**signup_url** | string | Optional | Public |
|**state** | string | Optional | Public |

#### SessionSpeaker

| Field | Datatype | Requirement |
| --- | --- | --- |
|**id** | integer | Required |
|**name** | string | Optional |
|**organisation** | string | Optional |


#### SessionTrack

| Field | Datatype | Requirement |
| --- | --- | --- |
|**id** | integer | Required |
|**name** | string | Optional |


#### SessionMicrolocation

| Field | Datatype | Requirement |
| --- | --- | --- |
|**id** | integer | Required |
|**name** | string | Optional |


#### SessionType

| Field | Datatype | Requirement |
| --- | --- | --- |
|**id** | integer | Required |
|**name** | string | Required |


### 4. Speaker

| Field | Datatype | Requirement | Access |
| --- | --- | --- | --- |
|**id** | integer | Required | Public |
|**name** | string | Required | Public |
|**email** | string | Required | Public |
|**short_biography** | string | Optional | Public |
|**long_biography** | string | Optional | Public |
|**organisation** | string | Required | Public |
|**country** | string | Required | Public |
|**mobile** | string | Optional | Public |
|**website** | string | Optional | Public |
|**github** | string | Optional | Public |
|**photo** | string | Optional | Public |
|**position** | string | Optional | Public |
|**facebook** | string | Optional | Public |
|**twitter** | string | Optional | Public |
|**linkedin** | string | Optional | Public |
|**sessions** | Array[**SpeakerSession**] | Optional | Public |


#### SpeakerSession

| Field | Datatype | Requirement |
| --- | --- | --- |
|**id** | integer | Optional |
|**title** | string | Optional |


### 5. Sponsor

| Field | Datatype | Requirement | Access |
| --- | --- | --- | --- |
|**id** | integer | Required | Public |
|**name** | string | Required | Public |
|**description** | string | Optional | Public |
|**url** | string | Optional | Public |
|**logo** | string | Optional | Public |
|**level** | string | Optional | Public |
|**sponsor_type** | string | Optional | Public |


### 6. Track

| Field | Datatype | Requirement | Access |
| --- | --- | --- | --- |
|**id** | integer | Required | Public |
|**name** | string | Required | Public |
|**description** | string | Optional | Public |
|**color** | string | Required | Public |
|**track_image_url** | string | Optional | Public |
|**location** | string | Optional | Public |
|**sessions** | Array[**TrackSession**] | Optional | Public |

#### TrackSession

| Field | Datatype | Requirement |
| --- | --- | --- |
|**id** | integer | Required |
|**title** | string | Optional |


### 7. User

| Field | Datatype | Requirement | Access |
| --- | --- | --- | --- |
|**id** | integer | Required | Public |
|**email** | string | Required | Public |
|**signup_at** | string | Optional | Public |
|**last_accessed_at** | string | Optional | Public |
|**user_detail** | **UserDetail** | Optional | Public |

#### UserDetail

| Field | Datatype | Requirement |
| --- | --- | --- |
|**firstname** | string | Optional | Public |
|**lastname** | string | Optional | Public |
|**details** | string | Optional | Public |
|**contact** | string | Optional | Public |
|**avatar** | string | Optional | Public |
|**facebook** | string | Optional | Public |
|**twitter** | string | Optional | Public |
