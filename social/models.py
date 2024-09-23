from django.contrib.gis.db import models
from core.models import Restaurant
from users.models import TimeStampedModel, User
from django.contrib.gis.geos import Point


# Create your models here.
def post_pic_dir(instance, filename):
    return f'Social/Post/{instance.user.id}_{filename}'


class Post(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)
    post_image = models.ImageField(blank=True, null=True, upload_to=post_pic_dir)
    content = models.TextField()
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    location_point = models.PointField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.location_point = Point(self.longitude, self.latitude)
        super(Post, self).save(*args, **kwargs)

    @property
    def comment_counts(self):
        return self.comments.all().count()

    @property
    def like_counts(self):
        return self.likes.all().count()


class FollowRequest(TimeStampedModel):
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_followers', blank=True, null=True)
    follower = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name='user_following', null=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        unique_together = (('following', 'follower'),)
        indexes = [
            models.Index(fields=['following']),
        ]


class Like(TimeStampedModel):
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        unique_together = (('post', 'liked_by'),)
        indexes = [
            models.Index(fields=['post']),
        ]


class Comment(TimeStampedModel):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    comment_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['post']),
        ]


def event_pic_dir(instance, filename):
    return f"Social/Event/{instance.created_by.id}_{filename}"


class Event(TimeStampedModel):
    restaurant = models.ForeignKey(Restaurant, related_name='events', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    event_image = models.ImageField(blank=True, null=True, upload_to=event_pic_dir)
    date_time = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, related_name='created_events', on_delete=models.CASCADE, blank=True, null=True)
    is_approved_by_restaurant = models.BooleanField(default=False)

    @property
    def participants_counts(self):
        return self.participants.all().count()


class Participant(TimeStampedModel):
    event = models.ForeignKey(Event, related_name='participants', on_delete=models.CASCADE, null=True, blank=True)
    participated_by = models.ForeignKey(User, related_name='participated', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = (('event', 'participated_by'),)
        indexes = [
            models.Index(fields=['event']),
        ]
