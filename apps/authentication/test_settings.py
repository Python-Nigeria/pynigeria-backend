from pynigeriaBackend.settings import *

REST_FRAMEWORK = {
    "REST_FRAMEWORK_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "5000/min",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "pynigeriaBackend.exception_handler.pynigeria_exception_handler",
}
