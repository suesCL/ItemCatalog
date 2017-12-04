# ItemCatalog 

## Overview 
ItemCatalog is a web app that displays items and their catagories and allows authorized user to perform CRUD operation on them.
The app implements JSON endpoints that serve information as displayed in HTML endpoints.
The app also implements third-party authentication and authorization service for any CRUD operation execution.


The app utilizes Flask framework for routing and templating and employs SQLite database. 

## Implementation
* **API Endpoints** 
  * Query data from database with session object 
  * Serialize returned data
  * Use jsonify method to convert JSON output into a Response objecct with the application/json mimetype

* **User Registration**
  * Create a button for sign-up
  * Extract form information and check if it exists in database. If the user information does not exist, add an new user to daabase. 
  * Generate auth token to web page
  
* **Google login**
  * Parse auth code
  * Exchange for an access token 
  * Find the user
  * Make token

* **Authenticae user**
  * Created verify_password function to check the username or token and password. 
  * Check to see if the database has the user by verifying auth token or username

* **CRUD**
Add **@auth.login_required** decorator at the begining of each CRUD method to ensure authorization and authentication 

## Installation

## References
