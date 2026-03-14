from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Segurança ─────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY',
    'troque-isso-antes-de-ir-para-producao-use-variavel-de-ambiente')

DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost 127.0.0.1').split()

# ── Apps ──────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Segurança
    'axes',

    # Projeto
    'accounts',
    'contratos',
    'empresas',
    'mobilizacao',
    'financeiro',
]

# ── Middleware ────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',       # arquivos estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'axes.middleware.AxesMiddleware',                   # bloqueio de brute force
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'core.wsgi.application'

# ── Banco de dados ────────────────────────────────────────────────────────────
# SQLite com WAL mode — suporta múltiplos leitores simultâneos sem travar
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,
            'init_command': (
                'PRAGMA journal_mode=WAL;'      # múltiplos leitores simultâneos
                'PRAGMA synchronous=NORMAL;'    # mais rápido, ainda seguro
                'PRAGMA cache_size=-64000;'     # 64MB de cache
                'PRAGMA foreign_keys=ON;'       # integridade referencial
                'PRAGMA temp_store=MEMORY;'     # temp tables em RAM
            ),
        },
    }
}

# ── Autenticação ──────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL           = '/accounts/login/'
LOGIN_REDIRECT_URL  = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Sessão expira ao fechar o browser + timeout de 8h
SESSION_COOKIE_AGE      = 28800          # 8 horas em segundos
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True           # JS não acessa o cookie
SESSION_COOKIE_SAMESITE = 'Lax'

# ── django-axes — bloqueio de brute force ─────────────────────────────────────
AXES_FAILURE_LIMIT       = 5            # bloqueia após 5 tentativas erradas
AXES_COOLOFF_TIME        = 1            # desbloqueia após 1 hora
AXES_LOCKOUT_TEMPLATE    = 'accounts/bloqueado.html'
AXES_RESET_ON_SUCCESS    = True         # reseta contador ao logar com sucesso
AXES_ENABLE_ADMIN        = True
AXES_IPWARE_PROXY_COUNT  = 1

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# ── Segurança HTTP ────────────────────────────────────────────────────────────
# Ativado apenas em produção (DEBUG=False)
if not DEBUG:
    SECURE_HSTS_SECONDS            = 31536000   # 1 ano
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD            = True
    SECURE_SSL_REDIRECT            = True
    SESSION_COOKIE_SECURE          = True       # cookie só via HTTPS
    CSRF_COOKIE_SECURE             = True
    SECURE_BROWSER_XSS_FILTER     = True
    SECURE_CONTENT_TYPE_NOSNIFF    = True
    X_FRAME_OPTIONS                = 'DENY'

CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# ── Internacionalização ───────────────────────────────────────────────────────
LANGUAGE_CODE = 'pt-br'
TIME_ZONE     = 'America/Sao_Paulo'
USE_I18N      = True
USE_TZ        = True

# ── Arquivos estáticos ────────────────────────────────────────────────────────
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Logs de segurança ─────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} — {message}',
            'style': '{',
        },
    },
    'handlers': {
        'arquivo_seguranca': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'seguranca.log',
            'maxBytes': 5 * 1024 * 1024,   # 5MB
            'backupCount': 3,
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'axes':    {'handlers': ['arquivo_seguranca', 'console'],
                    'level': 'WARNING'},
        'django.security': {'handlers': ['arquivo_seguranca', 'console'],
                            'level': 'WARNING'},
        'django.request':  {'handlers': ['console'],
                            'level': 'ERROR'},
    },
}