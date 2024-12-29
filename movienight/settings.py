"""
Django settings for movienight project.


Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import json
import sys
from configurations import Configuration, values
import base64
from firebase_admin import credentials, initialize_app
from datetime import timedelta
import dj_database_url

from dotenv import load_dotenv

load_dotenv()

class Dev(Configuration):
    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


    # Quick-start development settings - unsuitable for production
    # See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = 'yqz=f3duzu3s5n2%jg#r5+(l!hb8vxwz)5fuij5h=_+t3u!nhs'

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = values.BooleanValue(True)

    # ALLOWED_HOSTS = values.ListValue(["localhost", "0.0.0.0", "127.0.0.1", "9994-2a02-8428-81a3-a701-d871-ed23-88ac-5677.ngrok-free.app"])
    ALLOWED_HOSTS = [
        'web-production-5212b.up.railway.app', 
        'localhost',
        '127.0.0.1',
        '0.0.0.0'
    ]
    CSRF_TRUSTED_ORIGINS = [
        'https://web-production-5212b.up.railway.app', 
    ]
    AUTH_USER_MODEL = "movienight_auth.User"


    # Application definition

    INSTALLED_APPS = [
        # Django core apps
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',

        # Third-party apps
        'corsheaders',
        'rest_framework',
        'rest_framework_simplejwt',
        'drf_spectacular',
        'djoser',
        'apps.movienight_auth',  # Contains custom user model
        "django_celery_results",
        "django_celery_beat",
        'django_filters',

        # Other custom apps
        'apps.movies',
        "apps.notifications",
        "apps.chat",
        "apps.movienight_profile",
        "debug_toolbar"
    ] 
    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
    ]

    ROOT_URLCONF = 'movienight.urls'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(BASE_DIR, "templates")],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]

    WSGI_APPLICATION = 'movienight.wsgi.application'


    # Database configuration
    DATABASES = {}

    if os.getenv('USE_SQLITE_FOR_TESTS') == 'True' or 'pytest' in sys.argv:
        # Use SQLite for tests
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(BASE_DIR, 'test_db.sqlite3'),
            }
        }
        CELERY_TASK_ALWAYS_EAGER = True
        CELERY_TASK_EAGER_PROPAGATES = True
    elif os.getenv('DATABASE_URL'):
        # Use DATABASE_URL for development/production
        DATABASES = {
            'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
        }
    else:
        # Fallback to a hardcoded development database
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'dev_db',
                'USER': 'dev_user',
                'PASSWORD': 'dev_password',
                'HOST': 'db',
                'PORT': '5432',
            }
        }

    # Password validation
    # https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
    # https://docs.djangoproject.com/en/3.0/topics/i18n/

    LANGUAGE_CODE = 'en-us'

    TIME_ZONE = values.Value('Europe/Paris')

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True


    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/3.0/howto/static-files/

    STATIC_URL = '/static/'

    
    REST_FRAMEWORK = {
        "DEFAULT_SCHEMA_CLASS": 'drf_spectacular.openapi.AutoSchema',
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework.authentication.BasicAuthentication",
            "rest_framework.authentication.SessionAuthentication",
            "rest_framework.authentication.TokenAuthentication",
            "rest_framework_simplejwt.authentication.JWTAuthentication"
        ],
        # "DEFAULT_THROTTLE_CLASSES": [
        #     "movies.throttlings.AnonSustainedThrottle",
        #     "movies.throttlings.AnonBurstThrottle",
        #     "movies.throttlings.UserSustainedThrottle",
        #     "movies.throttlings.UserBurstThrottle",
        # ],
        # "DEFAULT_THROTTLE_RATES": {
        #     "anon_sustained": "500/day",
        #     "anon_burst": "10/minute",
        #     "user_sustained": "5000/day",
        #     "user_burst": "100/minute",
        # },
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
        "PAGE_SIZE": 20,
        "DEFAULT_FILTER_BACKENDS": [
            "django_filters.rest_framework.DjangoFilterBackend",
            "rest_framework.filters.OrderingFilter"
        ],
    }


    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID') 
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    
    DJOSER = {
        "USER_ID_FIELD": "email",
        "LOGIN_FIELD": "email",
        "SEND_ACTIVATION_EMAIL": False,
        "ACTIVATION_URL": 'auth/users/activate/{uid}/{token}/',
        "PASSWORD_RESET_CONFIRM_URL": 'auth/password/reset/confirm/{uid}/{token}/',
        "PASSWORD_RESET_CONFIRM_RETYPE": True,
        "USER_CREATE_PASSWORD_RETYPE": True
    }
    SIMPLE_JWT = {
        'ACCESS_TOKEN_LIFETIME': timedelta(days=2),
        "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    }
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    # CORS      
    # CORS_ALLOWED_ORIGINS = [ 
    #     "http://localhost:5173",
    #     "http://localhost",
    #     "https://movie-night-ui.vercel.app" 
    # ]
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True # Credentials (cookies, authorization headers) can be included in cross-origin requests

    SPECTACULAR_SETTINGS = {
        "TITLE": "Movie Night",
        'DESCRIPTION': 'API for Movie Night',
        'VERSION': '1.0.0',
        'SECURITY': [
            {'BearerAuth': []},
            {'BasicAuth': []},
            ],
        'SECURITY_SCHEMES': {
            'BearerAuth': {
                'type': 'http',               
                'scheme': 'bearer',           
                'bearerFormat': 'JWT',        
                'description': 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer <token>"',
            },
            'BasicAuth': {
                'type': 'http',
                'scheme': 'basic',
                'description': 'Basic authentication with email and password.'
            },
        },
        'SECURITY_DEFINITIONS': {
            'Token': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
            },
            'Basic': {
                'type': 'basic',
            },
        },  
    }
    BASE_URL =  os.getenv('BASE_URL') 

    CELERY_BROKER_URL = 'redis://redis:6379/0'  # Directly connect to Redis via Docker network
    CELERY_RESULT_BACKEND = 'redis://redis:6379/0'


    # ABLY
    ABLY_API_KEY = os.getenv('ABLY_API_KEY')

    #Firebase
    # Get the base64-encoded Firebase key from the environment
    firebase_key_base64 = os.getenv('FIREBASE_ADMINSDK_KEY')

    # Decode the key from base64
    firebase_key_json = base64.b64decode(firebase_key_base64).decode('utf-8')

    # Convert the JSON string back to a dictionary
    firebase_cred_dict = json.loads(firebase_key_json)

    # Initialize Firebase Admin SDK using the decoded credentials
    cred = credentials.Certificate(firebase_cred_dict)
    initialize_app(cred, {
        'storageBucket': 'movie-night-609e1.appspot.com'  
    })

    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

    OMDB_KEY = os.getenv('OMDB_KEY', "e1406b6f")

    CACHE_TTL = 60 * 60
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.getenv('REDIS_URL_CACHE', 'redis://redis:6379/1'),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
            "TIMEOUT": CACHE_TTL
        }        
    }

    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"

    import os
    import socket

    # Dynamically configure INTERNAL_IPS for Django Debug Toolbar
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = ['127.0.0.1', '::1'] + [ip[: ip.rfind('.') + 1] + '1' for ip in ips]


class Prod(Dev):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DEBUG = values.BooleanValue(False)
    # SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
    DATABASES = values.DatabaseURLValue(f"sqlite:///{BASE_DIR}/db.sqlite3")
    #Database configuration
    if 'pytest' in sys.argv or os.getenv('USE_SQLITE_FOR_TESTS') == 'True':
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(BASE_DIR, 'test_db.sqlite3'),  
            }
        }
        CELERY_TASK_ALWAYS_EAGER = True
        CELERY_TASK_EAGER_PROPAGATES = True
    else:
        DATABASES = {
            'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
        }

    # CELERY 
    CELERY_RESULT_BACKEND = "django-db" # Store the results of tasks in the Django database
    CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://redis:6379/0')

    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'