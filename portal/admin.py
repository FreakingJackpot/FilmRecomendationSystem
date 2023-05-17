from django.contrib import admin
from portal.models import CustomUser, ServiceUser

admin.site.register(CustomUser)


@admin.register(ServiceUser)
class ServiceUserAdmin(admin.ModelAdmin):
    list_display = ["username", 'approved']
