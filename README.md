# Alumni-Network
This is a django based website to store and maintain basic information about college alumni like their city of recedence and company they work for.

## Getting Started
  1. Create a virtual environment and set default python version to 3.8:
  ```shell
    mkvirtualenv env --python=/usr/bin/python3.8
  ```
  Refer [this](https://virtualenvwrapper.readthedocs.io/en/latest/) if not familiar with python virtual environments
  
  2. Install django's latest version:
  ```shell
    pip install django
  ```
  3. Clone this project
  4. Create two subdirectories "people" and "companies" in the root directory of the project
     This is where markdown entries will be stored(refer to utils.py file in network app directory)
  5. Open the alumni directory and create a file name ".env". Create two environment variables "HOST" and "SECRET_KEY" for 
     sedning emails, using python decouple. Refer [this](https://pypi.org/project/python-decouple/) if not familiar with decouple
     and environment variables in general
  6. You need to set the site id for the domain on which you will be deploying this project
     Go to django admin shell with:
     ```shell
       python manage.py shell
     ```
     and add your domain to the database:
     ```shell
        from django.contrib.sites.models import Site
        site = Site(domain="yourdomain.com", name="name_you_are_gonna_use_for_this_site")
        site.save()
     ```
     multiple domains can be added in this manner, get the value of this site's id with:
     ```shell
        site.id
     ```
     
     Add this value in the as SITE_ID in the settings.py file. Avoiding this step will generate links just for "example.com"
     and not to your domain, thus the auth token generated won't matter.
     
## Dependencies
  All the dpendencies of this project are in requirements.txt
  while in root directory(and the virtual environment active), run:
  ```shell
    python -m pip install -r requirements.txt
  ```
  
  It will install:
  1. django-markdown2
  Which is utilized in rendering html from markdown entries
  2. django-crispy-forms
  which contains Jinja template tags to genrate CSS for forms generated by django.
  3. python-decouple
  Which is used to create environment variables to store sensitive data used while executing functionalities
  
  
## About markdown files:
Storing data in the form of markdown files can be completely avoided, this has been implemented just because gathering
information about all the batches which have passed out of college is a long process and it can be extremely costly
if the person managing the admin site messes up and looses data, or while implementing a new model, there is an Integrity
error of some sort due to previously performed migrations.

Storing all the information in the form of markdown files as well as sqlite database ensures that in the event where the database
somehow malfunctions, superusers will still have access to all the markdwon files, which follow the same pattern, thus making it
possible to retrieve the data back.


run
```shell
  python manage.py runserver
```
to start the website on local machine.
Note that while deploying the website it is unsafe to keep "debug=True" in the settings.py file, and when "debug=False", 
the static files used in html templates(css and javascript) should be managed by the domain provider and not by the
django "static" tag.
