"""Configuration settings for the hpath app."""

REDIS_HOST = 'redis'  # or name of docker service in same network
"""Hostname for the Redis server."""

REDIS_PORT = 6379
"""Port for the Redis server, default 6379 for unaltered Docker container
(https://hub.docker.com/_/redis)."""

HPATH_SIM_HOST = 'hpath-restful'
"""Path to the histopathology simulation server."""

HPATH_SIM_PORT = '5000'
"""Port for the histopathology simulation server."""

SENSOR_HOST = 'http://129.169.49.180/api/sensorsdt/'
