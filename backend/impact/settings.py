"""
Django settings for impact project.

Generated by 'django-admin startproject' using Django 3.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from social_core.backends.open_id import OpenIdAuth
from social_core.exceptions import AuthMissingParameter
from django.contrib.messages import constants as message_constants

from pathlib import Path

import os, sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_ROOT = Path(BASE_DIR) / "media"
MEDIA_URL = "/media/"
IMG_THUMBNAIL_SIZE = (600, 400);

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/



ALLOWED_HOSTS = ["localhost", "127.0.0.1", "dev.citympact.ch", "dev2.citympact.ch", "www.citympact.ch", "citympact.ch"]


# Application definition

INSTALLED_APPS = [
    'mainApp.apps.MainappConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_django',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'mainApp.middleware.UserMiddleware',
]

ROOT_URLCONF = 'impact.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'mainApp.apps.constant_variables_processor',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'impact.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'fr-ch'

TIME_ZONE = 'Europe/Zurich'

USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = Path(BASE_DIR) / "collected_static"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'




class SwissIDOpenId(OpenIdAuth):
    """SwissID OpenID authentication backend"""
    name = 'swissid'

    def openid_url(self):
        """Returns SwissID authentication URL"""
        for requiredKey in ["SWISS_ID_CLIENT_ID", "SWISS_ID_CLIENT_SECRET",
            "SWISS_ID_ENV"]:
            if not self.data.get(requiredKey):
                raise AuthMissingParameter(self, requiredKey)
        return "%s/idp/oauth2/authorize?response_type=code&client_id=%s&scope=openid%20profile&redirect_uri=%s&nonce=%s&state=%s&acr_values=loa-1&ui_locales=de" % (
            self.data["SWISS_ID_ENV"],
            self.data["SWISS_ID_CLIENT_ID"],
            "callback_url.html",
            "NONCE-TODO",
            "STATE?"
            )

try:
    DEBUG = (os.environ["DEBUG"].lower() == "true")

    # Google auth related keys:
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ["SOCIAL_AUTH_GOOGLE_OAUTH2_KEY"]
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = \
            os.environ["SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET"]
    # End of Google auth related keys:

    # mail related keys:
    for email_key in ["EMAIL_HOST", "EMAIL_PORT", "EMAIL_HOST_USER", "EMAIL_HOST_PASSWORD", "DEFAULT_FROM_EMAIL"]:
        globals()[email_key] = os.environ[email_key]
    EMAIL_USE_TLS = True

    # LinkedIn auth related keys:
    for email_key in ["SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY", "SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET"]:
        globals()[email_key] = os.environ[email_key]
    SOCIAL_AUTH_LINKEDIN_OAUTH2_SCOPE = ['r_liteprofile', 'r_emailaddress']
    SOCIAL_AUTH_LINKEDIN_OAUTH2_FIELD_SELECTORS = ['emailAddress']
    SOCIAL_AUTH_LINKEDIN_OAUTH2_EXTRA_DATA = [('id', 'id'),
                                          ('firstName', 'first_name'),
                                          ('lastName', 'last_name'),
                                          ('emailAddress', 'email_address')]

    # Facebook auth related keys:
    for email_key in ["SOCIAL_AUTH_FACEBOOK_KEY", "SOCIAL_AUTH_FACEBOOK_SECRET"]:
        globals()[email_key] = os.environ[email_key]
    SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
    SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
      'locale': 'fr_FR',
      'fields': 'id, name, email, age_range'
    }

    SECRET_KEY = os.environ["SECRET_KEY"]
    CITY_NAME = os.environ["CITY_NAME"]

except KeyError as e:
    print("Unable to find the necessary API key in the environment variables.")
    print("Missing environment variable: %s." % e)
    sys.exit(-1)


AUTHENTICATION_BACKENDS = (
    'social_core.backends.open_id.OpenIdAuth',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.linkedin.LinkedinOAuth2',
    'social_core.backends.apple.AppleIdAuth',
    'social_core.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# We associate the accounty by email (read the risk about temporary account).
# This guarantees that if the account has been created beforehand, the SSO login
# won't create a duplicate.
#
# The default user-details population strategy is replaced below by a custom
# pipeline function that updates account fileds only if they had an empty
# content (see mainApp.pipeline.update_user_data).
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    #'social_core.pipeline.user.user_details',
    'mainApp.pipeline.update_user_data'
)



# Todo: setup SMTP mailing here:
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_FILE_PATH = str(BASE_DIR.joinpath('sent_emails'))


# Adapting the message severities to match Bootstrap CSS classes:
MESSAGE_TAGS = {message_constants.DEBUG: 'debug',
                message_constants.INFO: 'info',
                message_constants.SUCCESS: 'success',
                message_constants.WARNING: 'warning',
                message_constants.ERROR: 'danger',}


LOGIN_REDIRECT_URL = "/"
SOCIAL_AUTH_LOGIN_REDIRECT_URL = LOGIN_REDIRECT_URL
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = "/accounts/profile/"
