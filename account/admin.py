from django.contrib import admin
from parler.admin import TranslatableAdmin

from account.models import CustomUser, ServiceUser, Occupation

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Occupation, TranslatableAdmin)


@admin.register(ServiceUser)
class ServiceUserAdmin(admin.ModelAdmin):
    list_display = ["username", 'approved']
