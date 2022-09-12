from concurrent.futures import thread


wsgi_app = 'wsgi:app'
bind = '0.0.0.0:8000'

workers = 1
# threads = 2
max_requests = 2040

loglevel = 'debug'
accesslog = errorlog =  "-"
capture_output = True

timeout = 30
keepalive = 2
# reload

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")