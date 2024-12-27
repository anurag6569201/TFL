from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['https://tfl2k24.azurewebsites.net','http://127.0.0.1:8000/','*','https://theflavourlake.in/','.vercel.app']
CSRF_TRUSTED_ORIGINS = ['https://tfl2k24.azurewebsites.net','http://127.0.0.1','https://theflavourlake.in']

# Application definition
INSTALLED_APPS = [
    'jazzmin',

    'django.contrib.admin',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'home',
    'home.templatetags',
    'background_task',

    'compressor',
    'htmlmin', # html minify for production

    'import_export',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    "allauth.account.middleware.AccountMiddleware",

    "whitenoise.middleware.WhiteNoiseMiddleware", # deployment middleware

    # html minify for production
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',
]
HTML_MINIFY = True 
ROOT_URLCONF = 'tfl.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
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

WSGI_APPLICATION = 'tfl.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT=os.path.join(BASE_DIR,'staticfiles')
STATICFILES_DIRS=[os.path.join(BASE_DIR,'static')]
MEDIA_URL='/media/'
MEDIA_ROOT=os.path.join(BASE_DIR,'media')


STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_URL = STATIC_URL
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'sass --scss {infile} {outfile}'),
)



# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '587'
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER_EMAIL")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_USER_PASSWORD")
EMAIL_USE_TLS=True
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
LOGIN_REDIRECT_URL = '/'

RAZORPAY_KEY=os.getenv("RAZORPAY_TESTING_KEY")
RAZORPAY_SECRET=os.getenv("RAZORPAY_TESTING_SECRET")

SESSION_COOKIE_AGE = 300 # 5 MINS
SESSION_SAVE_EVERY_REQUEST = True


JAZZMIN_SETTINGS = {
    "site_title": "The Flavour Lake",
    "site_header": "TFL Dashboard",
    "site_brand": "TFL",
    "site_logo": "../static/assets/img/home/tfl_logo.webp",  # Customize with your company's logo
    "login_logo": "../static/assets/img/home/tfl_logo.webp",
    "welcome_sign": "Welcome to TFL Admin Panel",
    "copyright": "theflavourlake © 2024",
    "user_avatar": "profile.picture",  # Assuming you have a user profile picture field


    # Footer Links
    "footer_links": [
        {"name": "The Flavour Lake", "url": "https://theflavourlake.in", "new_window": True},
        {"name": "Support", "url": "mailto:support@theflavourlake5@gmail.com", "new_window": True},
    ],
}
