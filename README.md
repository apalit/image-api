# Image Management System
Rest APIs written in Django Rest framework to upload images and generating thumbnails

# Setup
The project has been set up to run with docker. It uses Postgres database and celery to run asynchronous tasks

Run the following commands from the base directory of the project

 - To start the project in detached mode

```commandline
docker-compose up -d --build
```
- Run migrate to create the data model
```
# if the application is already up
docker-compose exec web python manage.py migrate
# if the application is not running
docker-compose run web python manage.py migrate

```
- To create admin user
```commandline
docker-compose exec web  python manage.py createsuperuser 
```
- To run fixture for default plans
```commandline
docker-compose exec web  python manage.py loaddata default_plans.json
```
- To run tests
```
docker-compose run web pytest .
```
The admin application is accessible at http://localhost:8000/admin. 

Following endpoints are available
* `POST /api/images/` - To upload an image
* `GET /api/images/` - To view all images including thumbnails, available to the user 
* `GET /api/images/<id>/` - To fetch the details of an image by id.

User needs to be logged in to access the images and also subscribed to a plan. The users and plans will be created using the Admin web.
Fixtures can be added for the default plans. The default rest framework endpoint `api-auth/login/` has been enabled for ease of login.
The thumbnails are created based on plan asynchronously, using celery and redis.

# Assumptions made:
* The links of images with no expiry set, are always available.
* The images whose expiry has been set, become unavailable in API after the expiry period. They won't be retrieved by the GET api/images endpoint.

# To do:
* Caching
* More Testing
* Documentation

# Further enhancements
* Can use a different backend to store images, say S3.
* Automated script or Makefile can be used to run the various commands.
* Various tools, such as flake8, bandit, etc can be incorporated to run in test environment (eg, using tox) or as pre-commit hooks. 
