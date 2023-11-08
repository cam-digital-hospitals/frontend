"""Configuration settings for the hpath app."""

REDIS_HOST = 'redis'
"""Hostname for the Redis server."""

REDIS_PORT = 6379
"""Port for the Redis server, default 6379 for unaltered Docker container
(https://hub.docker.com/_/redis)."""

HPATH_RESTFUL_HOST = 'http://hpath-restful:5000/'
"""Path to the histopathology REST server."""

SENSOR_HOST = 'http://129.169.49.180/api/sensorsdt/'
"""Path to the sensor IoT server."""

TAT_TARGET = {'7': 0.8, '10': 0.9, '12': 0.95, '21': 0.95}
"""TAT target: proportion of specimens done in {n} days."""

LAB_TAT_TARGET = {'3': 0.8}
"""Lab TAT target: proportion of specimens done in {n} days."""
