## API Fields

Third level headers are main models (e.g. `Event`, `Session`, etc.). Fourth level headers are nested fields (e.g. `SessionSpeaker`, `TrackSession`, etc.).

Datatype, requirement and access-level has been defined for every model. Nested fields inherit the access-level defined for them in the model.

### Event

| Field | Datatype | Requirement | Access |
| --- | --- | --- | --- |
|**id** | integer | Required | Public |
|**event_url** | string | Optional | Public |
|**location_name** | string | Optional | Public |
|**description** | string | Optional | Public |
|**color** | string | Optional | Public |
|**start_time** | string | Required | Public |
|**longitude** | number | Optional | Public |
|**name** | string | Required | Public |
|**organizer_name** | string | Optional | Public |
|**background_url** | string | Optional | Public |
|**state** | string | Optional | Public |
|**email** | string | Optional | Public |
|**end_time** | string | Required | Public |
|**organizer_description** | string | Optional | Public |
|**latitude** | number | Optional | Public |
|**logo** | string | Optional | Public |
|**closing_datetime** | string | Optional | Public |


### Format

| Field | Datatype | Requirement | Access |
| --- | --- | --- | --- |
|**id** | integer | Required | Public |
|**label_en** | string | Optional | Public |
|**name** | string | Optional | Public |


### Languages

| Field | Datatype | Requirement | Access |
| --- | --- | --- | --- |
|**id** | integer | Required | Public |
|**label_de** | string | Optional | Public |
|**label_en** | string | Optional | Public |
|**name** | string | Optional | Public |


### Level

| Field | Datatype | Requirement | Access |
| --- | --- | --- | --- |
|**id** | integer | Required | Public |
|**label_en** | string | Optional | Public |
|**name** | string | Optional | Public |


### Microlocation

| Field | Datatype | Requirement | Access |
| --- | --- | --- | --- |
|**id** | integer | Required | Public |
|**name** | string | Optional | Public |
|**floor** | integer | Optional | Public |
|**longitude** | number | Optional | Public |
|**latitude** | number | Optional | Public |
|**room** | string | Optional | Public |


### Session

| Field | Datatype | Requirement | Access |
| --- | --- | --- | --- |
|**speakers** | Array[**SessionSpeaker**] | Optional | Public |
|**subtitle** | string | Optional | Public |
|**description** | string | Optional | Public |
|**language** | **SessionLanguage** | Optional | Public |
|**format** | **SessionFormat** | Optional | Public |
|**track** | **SessionTrack** | Optional | Public |
|**start_time** | string | Optional | Public |
|**title** | string | Optional | Public |
|**id** | integer | Required | Public |
|**microlocation** | **SessionMicrolocation** | Optional | Public |
|**end_time** | string | Optional | Public |
|**level** | **SessionLevel** | Optional | Public |
|**abstract** | string | Optional | Public |


#### SessionSpeaker

| Field | Datatype | Requirement |
| --- | --- | --- |
|**id** | integer | Required |
|**name** | string | Optional |


#### SessionLanguage

| Field | Datatype | Requirement |
| --- | --- | --- |
|**id** | integer | Required |
|**label_de** | string | Optional |
|**label_en** | string | Optional |


#### SessionFormat

| Field | Datatype | Requirement |
| --- | --- | --- |
|**id** | integer | Required |
|**name** | string | Optional |


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


#### SessionLevel

| Field | Datatype | Requirement |
| --- | --- | --- |
|**id** | integer | Required |
|**label_de** | string | Optional |
|**label_en** | string | Optional |



### Speaker

| Field | Datatype | Requirement | Access |
| --- | --- | --- | --- |
|**id** | integer | Required | Public |
|**web** | string | Optional | Public |
|**github** | string | Optional | Public |
|**name** | string | Optional | Public |
|**sessions** | Array[**SpeakerSession**] | Optional | Public |
|**photo** | string | Optional | Public |
|**twitter** | string | Optional | Public |
|**linkedin** | string | Optional | Public |
|**facebook** | string | Optional | Public |
|**organisation** | string | Optional | Public |
|**country** | string | Optional | Public |
|**position** | string | Optional | Public |
|**email** | string | Optional | Public |
|**biography** | string | Optional | Public |


#### SpeakerSession

| Field | Datatype | Requirement |
| --- | --- | --- |
|**id** | integer | Optional |
|**title** | string | Optional |


### Sponsor

| Field | Datatype | Requirement | Access |
| --- | --- | --- | --- |
|**id** | integer | Required | Public |
|**description** | string | Optional | Public |
|**url** | string | Optional | Public |
|**logo** | string | Optional | Public |
|**sponsor_type_id** | integer | Optional | Public |
|**name** | string | Optional | Public |


### SponsorType

| Field | Datatype | Requirement | Access |
| --- | --- | --- | --- |
|**id** | integer | Required | Public |
|**name** | string | Optional | Public |


### Track

| Field | Datatype | Requirement | Access |
| --- | --- | --- | --- |
|**id** | integer | Required | Public |
|**description** | string | Optional | Public |
|**sessions** | Array[**TrackSession**] | Optional | Public |
|**color** | string | Optional | Public |
|**track_image_url** | string | Optional | Public |
|**location** | string | Optional | Public |
|**name** | string | Optional | Public |

#### TrackSession

| Field | Datatype | Requirement |
| --- | --- | --- |
|**id** | integer | Required |
|**title** | string | Optional |

