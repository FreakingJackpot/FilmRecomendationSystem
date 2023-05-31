from rest_framework.throttling import UserRateThrottle


class ThousandPerHourUserThrottle(UserRateThrottle):
    rate = '1000/h'


class HundredPerHourUserThrottle(UserRateThrottle):
    rate = '100/h'