# Database

## Technologies Used

- postgresql
- mysql
- OAuth 2.0 Support (Authentication)
  - Google
  - Facebook
  - Twitter
  - etc. (for later)

## Python Packages

- Flask-SQLAlchemy

## Specifications

### Access Control List (ACL)

- Everyone
- Attendee
  - Access to submit feedback and rating
  - Access to save own timetable (optional)
- Moderators
  - Access to modify HasStart for any session in any track
- Speakers
  - Access to modify own session
- Track Organisers
  - Access to modify own track and sessions within tracks
- Organisers
  - Access to modify own events
- Root
  - All access

#### User Parameters

Use OAuth 2.0 to get data

- Full Name (required)
- E-Mail (required)
- Profile Description (optional)
- Photo (get from gravatar or oauth) (optional)
- Social Links (optional)

### Events Management

#### Parameters

- Event ID
- Title
- Description
- Location
- Logo
- Theme Color
- Event URL
- etc.

- Location / Room
  - Title
  - long
  - lat

### Schedule Management

#### Object Types

- Tracks
  - Track ID
  - Title
  - Description
  - Event ID
  - Location / Room
  - etc.
- Sessions
  - Session ID
  - Title
  - Description
  - Track ID
  - Start Date/Time
  - End Date/Time
  - HasStart
  - Speaker ID
  - Status
  - etc.
- Session/Speaker
  - Session ID
  - Speaker ID
- Feedback
  - Talk ID
  - Description
  - User ID
- Rating
  - Talk ID
  - Rating
  - User ID
- Timetable (Optional)
  - Talk ID
  - User ID

## TODO

- Implement OAuth / Users and ACL
  - Set up test cases
  - [SYNC with REST API] Set up sample data
- Implement Events
  - Set up test cases
  - [SYNC with REST API] Set up sample data
- Implement Schedule
  - Set up test cases
  - [SYNC with REST API] Set up sample data
- Implement Saving Drafts (Optional)

