import os
import redis
import subprocess
from datetime import datetime
from ConfigParser import RawConfigParser

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_DIR_LOGS = os.path.join(BASE_DIR, 'logs')

try:
    os.makedirs(BASE_DIR_LOGS)
except OSError:
    pass

# Config
config = RawConfigParser()
config.read(os.path.join(os.path.join(BASE_DIR, 'bitcoinjackpot'), 'settings.ini'))

# Environment Settings
SECRET_KEY = config.get('secrets', 'SECRET_KEY')
DEBUG = False if config.get('environment', 'ENVIRONMENT') == "PRODUCTION" else True
TEMPLATE_DEBUG = False if config.get('environment', 'ENVIRONMENT') == "PRODUCTION" else True
BUILD = "DEVELOPMENT"
BASE_DOMAIN = config.get('environment', 'BASE_DOMAIN')
IS_EDUCATIONAL = True
IS_EDUCATIONAL_AMOUNT = 25

# Bitcoin
SATOSHI_RATIO = 100000000
MINIMUM_BITCOIN_BET = float(0.0001)
BITCOIN_PRIVATE_ADDRESS = config.get('secrets', 'BITCOIN_PRIVATE_ADDRESS')
BITCOIN_JACKPOT_ADDRESS = config.get('secrets', 'BITCOIN_JACKPOT_ADDRESS')

# BCJP Round Settings
ROUND_WINNING_PERCENT = float(0.95)
ROUND_CUT_PERCENT = float(0.05)

# Redis
#REDIS_CLIENT = redis.Redis(unix_socket_path='/tmp/redis.sock')
REDIS_CLIENT = redis.StrictRedis(host='localhost', port=6379, db=0)
REDIS_ROUND_BETS = 'BCJP_ROUND_BETS'
REDIS_ROUND_LOCK = 'BCJP_ROUND_LOCK'
REDIS_ROUND_LOCK_COUNT = 'BCJP_ROUND_LOCK_COUNT'
REDIS_ROUND_CURRENT_ID = 'BCJP_ROUND_CURRENT_ID'
REDIS_ROUND_CURRENT_AMOUNT = 'BCJP_ROUND_CURRENT_AMOUNT'
REDIS_WITHDRAW_LOCK_PREFIX = 'BCJP_WITHDRAW_LOCK_PREFIX_'
REDIS_WITHDRAW_LOCK_COUNT = 'BCJP_WITHDRAW_LOCK_COUNT'

# Alias Words
ALIAS_WORDS = open(os.path.join(os.path.join(BASE_DIR, 'bitcoinjackpot'), 'alias_words.txt')).read().splitlines()

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bcjp',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'bcjp.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'bitcoinjackpot.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'bcjp.db'),
        #'ENGINE': config.get('database', 'DATABASE_ENGINE'),
        #'NAME': config.get('database', 'DATABASE_NAME'),
        #'USER': config.get('database', 'DATABASE_USER'),
        #'PASSWORD': config.get('database', 'DATABASE_PASSWORD'),
        #'HOST': config.get('database', 'DATABASE_HOST'),
        #'PORT': config.get('database', 'DATABASE_PORT'),
    }
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = False

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_DIR_LOGS, 'bcjp.log'),
            'when': 'H',
            'interval': 1,
            'backupCount': 0,
        },
        'warning_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_DIR_LOGS, 'bcjp_warning.log'),
            'when': 'H',
            'interval': 1,
            'backupCount': 0,
        }
    },
    'loggers': {
        'bcjp.file': {
            'handlers': ['file'],
            'level': 'INFO',
            #'propogation': True,
        },
        'bcjp.warning_file': {
            'handlers': ['warning_file', 'file'],
            'level': 'WARNING',
            #'propogation': True,
        },
    }
}