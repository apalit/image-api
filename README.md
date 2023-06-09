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
docker-compose run --rm web pytest .
```
The admin application is accessible at http://localhost:8000/admin. 

Following endpoints are available
* `POST /api/images/` - To upload an image
* `GET /api/images/` - To view all images including thumbnails, available to the user, in paginated way
* `GET /api/images/<id>/` - To fetch the details of an image by id.
* `GET /api/expiring-links/` - To fetch all the expiring links created by the user
* `GET /api/expiring-links/?base_image=<image id>` - To fetch all the expiring links of an image created by the user
* `POST /api/expiring-links/` - To create an expiring link
* `GET PUT DELETE /api/expiring-links/<expiring-link id>/` - To retrieve or update details (say expiry_in_seconds) of  a link
* `GET /media/....` - To fetch the actual image. This can be accessed by anonymous users

User needs to be logged in to access the image APIs and also subscribed to a plan. 
The default rest framework endpoint `api-auth/login/` has been enabled for ease of login.
A fixture has been provided to create the default plans. Additional plans can be added via Admin UI.
The thumbnails are created based on plan asynchronously, using celery and redis. 

The image urls are of the following format
- Original/base image - media/imageupload/<uuid 1>/<uuid 2.(png|jpeg|jpg)>
- Thumbnail image - media/thumbnail/<uuid 1>/<uuid 2.(png|jpeg|jpg)>
- Expiry link - media/exp/<uuid 1>/<uuid 2.(png|jpeg|jpg)>

Note that expiry links are just aliases to the actual base image which become unavailable after expiry time.


# Further improvements and enhancements
* Enable caching to cache the images. This can be done using AWS Cloudfront or Django caching framework. Care has to be taken while caching the expiring links.
* As of now, the list endpoints are paginated which can be optimised further. They can also incorporate caching.
* More unit tests can be added.
* Auto generation of API documentation, say using Swagger. 
* Can use a different backend to store images, say S3.
* Automated script or Makefile can be used to run the various commands.
* Various tools, such as flake8, bandit, etc can be incorporated to run in test environment (eg, using tox) or as pre-commit hooks. 
