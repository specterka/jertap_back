from django.contrib import admin
from admin_dashboard.models import AdminNotification, UserDisputeResolution

# Register your models here.
admin.site.register(AdminNotification)
admin.site.register(UserDisputeResolution)