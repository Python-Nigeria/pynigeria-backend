from config.settings.development import *

REST_FRAMEWORK = {
    "REST_FRAMEWORK_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "5000/min",
        "user": "5000/min",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "config.exception_handler.pynigeria_exception_handler",
}
