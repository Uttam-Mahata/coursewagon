# Gunicorn configuration file

# Python version
python_version = "3.11"

# Server socket
bind = "0.0.0.0:5555"  # IP and port to bind
backlog = 2048         # Maximum number of pending connections

# Worker processes
workers = 3            # Number of worker processes (2-4 x NUM_CORES recommended)
worker_class = "sync"  # Type of worker (sync, gevent, etc.)
worker_connections = 1000
timeout = 60           # Worker timeout in seconds
keepalive = 2         # Keepalive timeout

# Process naming
proc_name = "course_wagon"
pythonpath = "."



# SSL (uncomment if using HTTPS)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"



# Application
wsgi_app = "app:app"  # Format is "module_name:application_name"