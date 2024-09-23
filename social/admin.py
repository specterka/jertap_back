from django.contrib import admin

from social.models import FollowRequest, Event, Post, Like, Comment, Participant


# Register your models here.
@admin.register(FollowRequest)
class FollowRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'following', 'follower', 'is_approved']
    readonly_fields = ['created_at', 'modified_at',]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'restaurant', 'name', 'description', 'event_image', 'date_time', 'created_by', 'is_approved_by_restaurant']
    readonly_fields = ['created_at', 'modified_at', ]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'restaurant', 'post_image', 'content', 'latitude', 'longitude', 'location_point']
    readonly_fields = ['created_at', 'modified_at', ]


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'liked_by']
    readonly_fields = ['created_at', 'modified_at', ]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'content', 'comment_by']
    readonly_fields = ['created_at', 'modified_at', ]


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['id', 'event','participated_by']
    readonly_fields = ['created_at', 'modified_at', ]
