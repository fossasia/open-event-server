# REST APIs

## Technologies Used

- OpenAPI 2.0 ([Swagger](http://swagger.io))
- OAuth 2.0 Support (Authentication)
  - Google
  - Facebook
  - Twitter
  - etc. (for later)
- [JSON Web Tokens (JWT)](http://jwt.io) (Access)
- CORS (might need to enable this)

## Python Packages

- Flask
- Flask-RESTPlus and/or Connexion
- Flask-JWT
- etc.

## Specifications

To be converted to swagger specs.

### Auth

- Login
- Logout
- OAuth
- etc.

### Users Management (ACL)

#### Type of Roles

- Everyone
  - GET access to all schedule/track
- Attendee
  - POST access to owned schedule/rating, schedule/feedback, schedule/timetable
- Moderators
  - POST access to all schedule/start and schedule/end
- Speakers
  - POST access to owned schedule/session
- Track Organisers
  - POST access to all schedule/session
- Organisers
  - POST access to owned events
- Administrators
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

- Write the swagger definitions
- Set up the swagger ui
- Write/Generate the interfaces for the API
- Generate sample responses
- Set up test cases
- [SYNC with Database] Set up Auth
- [SYNC with Database] Implement the APIs