# impact
Impact project

## How to start the server
```
cd backend
pip3 install -r requirements.txt
python3 manage.py runserver
```

# Installing the demo data

For having a nice demo view, some synthetic data can be added to the database:
```
cd backend
./manage.py loaddata demoData.json
```
Then you should see the first entries. Note that the images are on purpose not
version controlled. Please use the admin-site to upload some dummy images.

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
