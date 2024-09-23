from django.db import models
from users.models import TimeStampedModel, User


# Create your models here.
class AdminNotification(TimeStampedModel):
    title = models.TextField(default='')
    message = models.TextField(default='')
    is_read = models.BooleanField(default=False)


class UserDisputeResolution(TimeStampedModel):
    query_by = models.ForeignKey(User, related_name='user_dispute', on_delete=models.CASCADE)
    query = models.TextField()
    replay = models.TextField(blank=True, null=True)
    is_resolved = models.BooleanField(default=False)