import multiprocessing

workers = multiprocessing.cpu_count() - 2  # So that locust can have 2 cores
threads = (multiprocessing.cpu_count() - 2) * 2
proc_name = "sqlitetest"
# Access log - records incoming HTTP requests
accesslog = "gunicorn.access.log"
# Error log - records Gunicorn server goings-on
errorlog = "gunicorn.error.log"
# Whether to send Django output to the error log
capture_output = True
# How verbose the Gunicorn error logs should be
loglevel = "info"

pidfile = "gunicorn.pid"
