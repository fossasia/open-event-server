The Event Dashboard will be having an **Event Setup Checklist** displayed. ([Issue #848](https://github.com/fossasia/open-event-orga-server/issues/848))

##### UI Sample
![capture](https://cloud.githubusercontent.com/assets/2404372/16109654/9b4da57a-33c7-11e6-9a75-a729d3e41156.PNG)

- Each wizard step gets a row
    - Basic Details
    - Sponsors
    - Session, Tracks, Rooms
    - Call for Speakers
    - Session Forms

**Color Changes and Icons**

- If the all essential elements have been filled in the widget background turns green and there is a tick at the end
- If some parts are missing, but some basic information is there, the widget background turns yellow and there must be a small friendly warning element
- If basic information is missing, the widget background turns red
- If form is not getting used, e.g. "Call for papers is turned off", the widget background turns gray

**States**

1. Basic details
	- **Yellow** - Event name, start time, end time, description are filled
	- **Green** - (Yellow) + Location + Organizer name + Organizer Description
1. Sponsor Details
	- **Red** - No sponsors are added
	- **Yellow** - Only one sponsor is added but data is incomplete
	- **Green** - At Least one sponsor with all details has been added
1. Session, Tracks, Rooms
	- **Grey** - If turned off
	- **Red** - If Either one of session, tracks rooms is missing
	- **Yellow** - if either of session, tracks has incomplete data (either color, title, duration missing)
	- **Green** - At Least One complete track, one complete session type, one complete room
1. Call for speakers
	- **Grey** - If turned off
	- **Yellow** - if no announcement added  (timings are compulsory )
	- **Green** - Announcement added (timings are compulsory )
1. Create sessions form
	- **Green** - IMO, this has only one state. As there always is some field force selected
