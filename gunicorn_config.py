# Configuration Gunicorn pour Iovag
bind = "127.0.0.1:8000"
workers = 2
worker_class = "sync"
timeout = 60
keepalive = 5
errorlog = "/home/mathurinchampemont/iovag/logs/gunicorn_error.log"
accesslog = "/home/mathurinchampemont/iovag/logs/gunicorn_access.log"
loglevel = "info"
