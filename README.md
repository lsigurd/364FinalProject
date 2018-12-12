
This application provides a form for the user to input a movie, a genre, and a rating (1-5) for that movie. After clicking submit, the resulting page has: 
	- A list of all the movies, ratings, and directors of those movies in the database
	- The user can update a rating of a movie on this page
	- A list of top actors in every movie in the database
The application also provides a form for the user to input a rating (1-5). After clicking submit, the page refreshes so that all the movies in the database with this rating show below the form. 

The Navigation contains these links:
-Movie Form: Original form
-See all Results: The resulting page discussed above
-Actors in DB: A list of actors in the database (can be deleted from the database here)
-Directors in DB: A list of directors in the database
-Genres + Directors: contains the number of directors per genre in the database

The application has the following routes, each of which renders the template listed here:
http://localhost:5000/ -> index.html
http://localhost:5000/result -> result.html
http://localhost:5000/actors -> actors.html
http://localhost:5000/directors -> directors.html
http://localhost:5000/genres -> genres.html

Code Requirements: 

**A user should be able to load http://localhost:5000 and see the first page they ought to see on the application.**

**Include navigation in base.html with links (using a href tags) that lead to every other page in the application that a user should be able to click on. (e.g. in the lecture examples from the Feb 9 lecture, like this)**

**Ensure that all templates in the application inherit (using template inheritance, with extends) from base.html and include at least one additional block.**

**Must use user authentication (which should be based on the code you were provided to do this e.g. in HW4).**

**Must have data associated with a user and at least 2 routes besides logout that can only be seen by logged-in users.** 

**At least 3 model classes besides the User class.**

**At least one one:many relationship that works properly built between 2 models.**

**At least one many:many relationship that works properly built between 2 models.**

**Successfully save data to each table.**

**Successfully query data from each of your models (so query at least one column, or all data, from every database table you have a model for) and use it to effect in the application (e.g. won't count if you make a query that has no effect on what you see, what is saved, or anything that happens in the app).**

**At least one query of data using an .all() method and send the results of that query to a template.**

**At least one query of data using a .filter_by(... and show the results of that query directly (e.g. by sending the results to a template) or indirectly (e.g. using the results of the query to make a request to an API or save other data to a table)**

**At least one helper function that is not a get_or_create function should be defined and invoked in the application.**

**At least two get_or_create functions should be defined and invoked in the application (such that information can be saved without being duplicated / encountering errors).**

**At least one error handler for a 404 error and a corresponding template.**

**Include at least 4 template .html files in addition to the error handling template files.**

**At least one Jinja template for loop and at least two Jinja template conditionals should occur amongst the templates.
 At least one request to a REST API that is based on data submitted in a WTForm OR data accessed in another way online (e.g. scraping with BeautifulSoup that does accord with other involved sites' Terms of Service, etc).**

**Your application should use data from a REST API or other source such that the application processes the data in some way and saves some information that came from the source to the database (in some way).
 At least one WTForm that sends data with a GET request to a new page.**

**At least one WTForm that sends data with a POST request to the same page. (NOT counting the login or registration forms provided for you in class.)**

**At least one WTForm that sends data with a POST request to a new page. (NOT counting the login or registration forms provided for you in class.)**

**At least two custom validators for a field in a WTForm, NOT counting the custom validators included in the log in/auth code.**

**Include at least one way to update items saved in the database in the application (like in HW5).**

**Include at least one way to delete items saved in the database in the application (also like in HW5).**

**Include at least one use of redirect.**

**Include at least two uses of url_for. (HINT: Likely you'll need to use this several times, really.)**

**Have at least 5 view functions that are not included with the code we have provided. (But you may have more!)**