# User Interface

## Home Page

- Upcoming Events
- Call for Papers
- Featured Speakers
- Sign up / Log in
- Get source code from github

## Login Page

- Sign in using Google, Facebook, Twitter
- Sign in using e-mail + password
- Forgot password?
- Sign up using e-mail
- If new user, send welcome e-mail (optional)

## Sign up using e-mail

- Ask for e-mail + password + verify password
- Send verification e-mail with link to activate account
- Non-activated accounts get deleted after 14 days
- Send welcome e-mail after activated (optional)

## Dashboard Page for all users / attendees

Note: All users can have create event or submit paper

- List of Events calling for speakers
- List of Events visible to user
- Direct to WebApp UI when selected event (unless Organiser / Track Organiser / Speaker role)
- Edit Profile
- Create Event
- Submit Paper
- Apply to be Moderator / Volunteer
- Apply to be a track organiser

## Create Event Wizard

- All users can create new events and become the organiser of that event
- Create a wizard flow
- Type of sessions allowed
- Import from Eventbrite (Optional)
- Include slug

## Call for Papers Page

- Once event has been created, call for papers page should be available
- Information regarding event
- Tracks / Type of Papers
- Speaker Sign in (follow Login / Sign up using e-mail)
- Go to Administration Page for Speakers (specifically to event's call for papers)

## Dashboard Page (Events) for Event Organisers

- Information regarding event (e.g. number of papers submitted / accepted, number of speakers submitted / accepted, pending invitation of speaker, etc)
- Schedule Overview
- Invite Speakers
- Edit Schedule
- Settings
  - Edit Information
  - Edit Tracks
  - Edit Roles / Access Control

## Dashboard Page for Track Organisers

- Schedule Overview
- Edit Schedule

## Dashboard Page for Speakers

- List of Events / Sessions currently submitting
- List of Events / Sessions currently pending
- List of Events / Sessions currently accepted
- List of Events / Sessions previously accepted
- List of Events / Sessions previously submitted
- List of Events calling for speakers

## Submit Paper Proposal Page

- All users can submit a paper and become a speaker of that event
- Create a wizard flow
- Copy from previous submitted/accepted session

## Scheduling Page (Scheduler)

- Event Administrator will be able to schedule all tracks
- Track Administrator will only be able to schedule owned track
- List of accepted sessions
- List of pending sessions
- List of rejected sessions
- Each session will be in draft, until administrator has accepted the session
- Calendar style with number of days of event
- Assign sessions into slots
- Auto-assign sessions into empty slots (optional)

## Event Page (WebApp UI)

- Theme Color
- Logo
- Schedule of an event
- Filtering sessions
- Build my session list

## Dashboard Page for Moderators (WebApp UI)

- List of sessions assigned to Moderator
- Upcoming sessions to start / stop
- Finished sessions
- Ability to link to organiser twitter

## TODO

- Set up bootstrap theme and home page
- [SYNC with REST API] Set up Sign Up / Login
- Set up dashboard page
- Set up create event page
- Set up call for papers
- Set up submit papers
- Set up Scheduler
- Set up WebApp (feature parity with Android)
- Set up Android App (feature parity with WebApp)