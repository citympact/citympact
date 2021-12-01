# How to deploy the project

1. Update the settings (`settings.py`):

```
DEBUG = True # No debug output to the browser.
ALLOWED_HOSTS = ["foo.com"] # add a list of allowed hosts.
```
2. Update the OAuth credentials (used in `settings.py`) in the environment
variables.

3. Email settings: todo: implement STMP registration
