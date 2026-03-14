# gunicorn.conf.py
import multiprocessing

# Workers = (2 x CPUs) + 1 — ideal para 10-50 usuários
workers    = (multiprocessing.cpu_count() * 2) + 1
worker_class = 'sync'
threads    = 2
timeout    = 60
keepalive  = 5

bind       = '0.0.0.0:8000'
accesslog  = 'logs/acesso.log'
errorlog   = 'logs/erro.log'
loglevel   = 'warning'

# Reinicia workers automaticamente para evitar memory leak
max_requests          = 1000
max_requests_jitter   = 100