"""Configuration settings for the hpath app."""

REDIS_HOST = 'redis'  # or name of docker service in same network
"""Hostname for the Redis server."""

REDIS_PORT = 6379
"""Port for the Redis server, default 6379 for unaltered Docker container
(https://hub.docker.com/_/redis)."""

HPATH_RESTFUL_HOST = 'http://hpath-restful:5000/'
"""Path to the histopathology REST server."""

SENSOR_HOST = 'http://129.169.49.180/api/sensorsdt/'
"""Path to the sensor IoT server."""
