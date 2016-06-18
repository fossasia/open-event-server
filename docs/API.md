## API Authentication

To get access token, send a POST request to `/api/v2/login` with email and password.

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
|**start_time** | string | Required | Public |
|**end_time** | string | Required | Public |
|**latitude** | number | Optional | Public |
|**longitude** | number | Optional | Public |
|**background_url** | string | Optional | Public |
|**state** | string | Optional | Public |
|**email** | string | Optional | Public |
|**organizer_name** | string | Optional | Public |
|**organizer_description** | string | Optional | Public |
|**type** | string | Optional | Public |
|**topic** | string | Optional | Public |
|**ticket_url** | string | Optional | Public |
|**closing_datetime** | string | Optional | Public |
|**creator** | **EventCreator** | Required | Public |

#### EventCreator

| Field | Datatype | Requirement |
| --- | --- | --- |
|**id** | integer | Required |
|**email** | string | Required |


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

| Field | Datatype | Requirement | Access |
| --- | --- | --- | --- |
|**id** | integer | Required | Public |
|**title** | string | Required | Public |
|**subtitle** | string | Optional | Public |
|**short_abstract** | string | Optional | Public |
|**long_abstract** | string | Required | Public |
|**comments** | string | Optional | Public |
|**start_time** | string | Required | Public |
|**end_time** | string | Required | Public |
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
|**biography** | string | Optional | Public |
|**organisation** | string | Required | Public |
|**country** | string | Required | Public |
|**web** | string | Optional | Public |
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
|**description** | string | Required | Public |
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
|**user_detail** | **UserDetail** | Optional | Public |

#### UserDetail

| Field | Datatype | Requirement |
| --- | --- | --- |
|**fullname** | string | Optional | Public |
|**details** | string | Optional | Public |
|**contact** | string | Optional | Public |
|**avatar** | string | Optional | Public |
|**facebook** | string | Optional | Public |
|**twitter** | string | Optional | Public |
