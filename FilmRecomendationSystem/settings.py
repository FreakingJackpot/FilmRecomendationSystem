import os
from pathlib import Path

from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-0ntgsxi992-e!jsa+hgl*2!vxoo=rb-+9iie^vm+sv6)*)wp&h'

DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework.authtoken',
    'drf_yasg',
    'portal',
    'account',
    'film_recommender.apps.FilmRecommenderConfig',
    'authentication',
    'crispy_forms',
    "corsheaders",
    'rosetta',
    'parler',
    'django_countries',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'login_required.middleware.LoginRequiredMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'FilmRecomendationSystem.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'FilmRecomendationSystem.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {

        'ENGINE': 'django.db.backends.postgresql_psycopg2',

        'NAME': 'postgres',

        'USER': 'postgres',

        'PASSWORD': 'postgres',

        'HOST': '127.0.0.1',

        'PORT': '5432',

    }
}

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

AUTH_USER_MODEL = 'account.CustomUser'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True
LANGUAGES = [
    ('en-us', 'English'),
    ('ru', 'Russian')
]
PARLER_LANGUAGES = {
    None: (
        {'code': 'en-us', },
        {'code': 'ru', },
    ),
    'default': {
        'fallbacks': ['en-us'],
        'hide_untranslated': False,
    }
}

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale'), ]
USE_TZ = True

STATIC_URL = 'static/'

# STATIC_ROOT = os.path.join(BASE_DIR, 'static')


STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'  # this is exactly the value 'apikey'
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'sss30112001@yandex.ru'

TMDB_API_KEY = '50fdb27edf69b6758b780ffa9fb5cc98'
TMDB_IMAGE_CDN = 'https://image.tmdb.org/t/p/original'
TMDB_FILES_URL = 'http://files.tmdb.org/p/exports/movie_ids_{month}_{day}_{year}.json.gz'

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGIN_REQUIRED_IGNORE_VIEW_NAMES = [
    'authentication:login',
    'authentication:reset_password',
    'authentication:password_reset_done',
    'authentication:password_reset_confirm',
    'authentication:password_reset_complete',
    'authentication:registration',
]
LOGOUT_REDIRECT_URL = LOGIN_URL

PREDICT_SERVICE_USERNAME = 'portal'
PREDICT_SERVICE_PASSWORD = 'portal123'

PREDICTOR_SERVICE_URL = 'http://127.0.0.1:5000/'
PREDICTOR_SERVICE_LOGIN_URL = PREDICTOR_SERVICE_URL + 'users/login'
PREDICTOR_SERVICE_PREDICT_URL = PREDICTOR_SERVICE_URL + 'predictor/'

CELERY_BROKER_URL = 'redis://127.0.0.1:6379'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379'
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

CORS_ALLOWED_ALL_ORIGINS = True

CHECKPOINTS_DIR = os.path.join(BASE_DIR, 'film_recommender', 'checkpoints')
MODEL_DIR = os.path.join(BASE_DIR, 'film_recommender', 'outputs', 'model')

TOP_K = 12

CELERY_BEAT_SCHEDULE = {
    "import_genres": {
        "task": "film_recommender.tasks.import_genres",
        "schedule": crontab(hour=8),
    },
    "import_movies": {
        "task": "film_recommender.tasks.import_movies",
        "schedule": crontab(hour=9),
    },
    "predict_daily_recommends": {
        "task": "film_recommender.tasks.predict_daily_recommends",
        "schedule": crontab(minute=0, hour=0),
    },
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'format': 'Token',
        }
    }
}

if not DEBUG:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

YOUTUBE_API_KEY = 'AIzaSyCZMDmw56BMqWXP1_nuRhJQ5sgXo9StKbM'
