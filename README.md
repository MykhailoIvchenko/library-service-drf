# Library service API
This project is a Django REST API for managing a library service simple 
operations including register, login for user, creating, adding, deleting 
books by admin, creating, observing, borrowings. 
The project is containerized using Docker and includes automatic API documentation 
with Swagger and Redoc.

## Installing using GitHub

Install PostgreSQL and create db

- git clone https://github.com/MykhailoIvchenko/library-service-drf.git
- cd library-service-drf
- python -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt
- set POSTGRES_HOST=<your db hostname>
- set POSTGRES_DB=<your db name>
- set POSTGRES_USER=<your db username>
- set POSTGRES_PASSWORD=<your db user password>
- set PGDATA=<your link to the pg data>
- set SECRET_KEY=<your secret key>
- `python manage.py migrate`
- `python manage.py runserver`

## Run with Docker (recommended way)

Install [Docker Desktop](https://docs.docker.com/desktop/) and launch it

- `docker-compose build`
- `docker-compose up`

## Getting access

- create user via /api/user/register
- get access token via /api/user/token

## Getting access as admin
- enter container docker exec -it <container_name> sh, 
- create superuser by the command `python manage.py createsuperuser`

## Features
- JWT authenticated
- Admin panel /admin/
- Documentation is located at api/doc/swagger of at api/doc/redoc
- Registration for a user
- Managing books by admin
- Observing books by any visitor
- Creating borrowings by a user
- Observing own borrowings by a regular user and filtering by activeness
- Observing any borrowings by an admin user and filtering by activeness and user_id
