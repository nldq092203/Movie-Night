"""
Throttle Classes:
- `AnonSustainedThrottle`: Limits anonymous users to 500 requests per day.
- `AnonBurstThrottle`: Limits anonymous users to 10 requests per minute.
- `UserSustainedThrottle`: Limits authenticated users to 5000 requests per day.
- `UserBurstThrottle`: Limits authenticated users to 100 requests per minute.

"""
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class AnonSustainedThrottle(AnonRateThrottle):
    scope = "anon_sustained"


class AnonBurstThrottle(AnonRateThrottle):
    scope = "anon_burst"


class UserSustainedThrottle(UserRateThrottle):
    scope = "user_sustained"


class UserBurstThrottle(UserRateThrottle):
    scope = "user_burst"

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""