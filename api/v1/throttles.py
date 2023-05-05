from rest_framework.throttling import UserRateThrottle


class OncePerHourUserThrottle(UserRateThrottle):
    rate = '1/h'


class ThousandPerHourUserThrottle(UserRateThrottle):
    rate = '1000/h'
