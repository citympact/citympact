# impact
Impact project

## How to start the server
```
cd backend
pip3 install -r requirements.txt
python3 manage.py runserver
```


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
