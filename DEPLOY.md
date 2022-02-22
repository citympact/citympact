# How to deploy the project

1. Update the env settings (using the template `backend/settings.env.template`).
2. Run the django migrations
3. Collect the static files
( `git pull origin main && ~/.virtualenvs/citympact/bin/python backend/manage.py collectstatic`)
