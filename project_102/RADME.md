##Day 1: Database Connection and User Authentication
- Established a connection to MySQL database using mysql.connector.
- Implemented user registration with plain-text password storage (for demonstration only).
- Created a login route that verifies user credentials against the database.
- Added input validation for username and password fields.

##Day 2: Dashboard and Session Management
- Created a dashboard route that requires user authentication.
- Implemented session management to keep users logged in across requests.
- Added logout functionality to clear the session.
- Updated templates to display the logged-in user's name on the dashboard.

##Day 3: API Endpoint and Error Handling
- Developed a /api/login endpoint that accepts JSON payload for authentication.
- Implemented error handling for database operations and input validation.
- Ensured that all database connections and cursors are properly closed after use.
- Added comments and documentation for better code readability and maintainability.

-------
#Steps to how to connect to the database and run the application:
#1. Ensure MySQL and Xampp is installed and running on your machine and make sure your port is set to 3307 or 3306 depends on what you in xampp.
#2. Create the database named "campus_incident_db" and tables using the provided SQL script.
#3. Install required Python packages: "requirements.txt".
#4. Run this script in terminal (python dp_connector.py) to start the Flask application.
#5. Access the application via http://localhost:5000 in your web browser.
#6. Use the registration page to create a new user, then log in to access the dashboard.
#7. Use the /test-db route to verify database connectivity.