# Citympact
Citympact is an open-source platform for enabling citizens engagement.

The goal of this web app is to provide functionality for public administrations (e.g. cities) to have their citizen
 - vote on public projects,
 - comment existing projects or
 - sign (and propose new) public petitions.


## Installing the project

Start by creating a copy of the template settings configuration from `backend/settings.env.template` and adding at least a `SECRET_KEY` variable (the others can be left blank for now).

This can be temporarily activated in your environment, if your copy is called for example `.env`, using the command:

```
source .env
```

### Dependencies (and virtual environment)
Optionally, you can create a virtual python environment (venv), before starting
the server:
```
pip3 install virtualenv
python3 -m venv .
source bin/activate
```
Now you should install the python dependencies:
```
pip3 install -r backend/requirements.txt
```

Finally you should make Django migrations, apply them and run the server:
```
cd backend
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver
```
To stop the server, simply use `[CTR] + [C]`. Optionally, deactivate your venv
(`deactivate`).

### Installing the demo data

For having a nice demo view, some synthetic data can be added to the database:
```
cd backend
python3 manage.py loaddata demoData.json
```
Then you should see the first entries. Note that the images are on purpose not
version controlled. Please use the admin-site to upload some dummy images.

### Accessing the admin-site

Django provides an admin site to manage your database. You need to create a
super user:
```
cd backend
python3 manage.py createsuperuser
```
Finally, open (and login to) the admin site: `localhost:8080/admin/`.

## Testing
Install selenium:
```
pip3 install selenium
```

Download the Chrome driver (`chromedriver`) via https://chromedriver.chromium.org/downloads

For example for Linux and my Chrome version 92:
```
cd tests/binaries/
wget https://chromedriver.storage.googleapis.com/92.0.4515.107/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
rm chromedriver_linux64.zip
```

Then the test suite can be run using:
```
cd tests
pip3 install -r requirements.txt
python3 main.py
```
