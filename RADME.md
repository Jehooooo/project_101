Day 1: Database Connection and User Authentication
- Established a connection to MySQL database using mysql.connector.
- Implemented user registration with plain-text password storage (for demonstration only).
- Created a login route that verifies user credentials against the database.
- Added input validation for username and password fields.

Day 2: Dashboard and Session Management
- Created a dashboard route that requires user authentication.
- Implemented session management to keep users logged in across requests.
- Added logout functionality to clear the session.
- Updated templates to display the logged-in user's name on the dashboard.
Day 3: API Endpoint and Error Handling

- Developed a /api/login endpoint that accepts JSON payload for authentication.
- Implemented error handling for database operations and input validation.
- Ensured that all database connections and cursors are properly closed after use.
- Added comments and documentation for better code readability and maintainability.