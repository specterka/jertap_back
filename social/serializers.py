from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.db import IntegrityError
from core.serializers import ReviewRestaurantSerializer
from users.models import User
from core.models import Restaurant, Review
from social.models import FollowRequest, Post, Comment, Like, Event


class UserSocialDataSerializer(serializers.ModelSerializer):
    following_count = serializers.ReadOnlyField()
    follower_count = serializers.ReadOnlyField()
    request_count = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'username', 'profile_image', 'bio', 'following_count', 'follower_count', 'request_count']


class FollowerDataSerializer(serializers.ModelSerializer):
    user_data = UserSocialDataSerializer(source='follower', read_only=True)
    request_id = serializers.ReadOnlyField(source='id')

    class Meta:
        model = FollowRequest
        fields = ['request_id', 'created_at', 'user_data']
        read_only_fields = ['follower', 'following']


class FollowingDataSerializer(serializers.ModelSerializer):
    user_data = UserSocialDataSerializer(source='following', read_only=True)
    request_id = serializers.ReadOnlyField(source='id')

    class Meta:
        model = FollowRequest
        fields = ['request_id', 'created_at', 'user_data']
        read_only_fields = ['follower', 'following']


class SearchUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile_image', 'bio']


class EditUserSocialProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_image', 'bio']


class SendFollowRequestSerializer(ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = FollowRequest
        fields = ['user_id']

    def validate_user_id(self, value):
        request = self.context.get('request')
        if value == request.user.id:
            raise serializers.ValidationError("You cannot follow yourself.")
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with id {value} does not exist.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        following_user = User.objects.get(id=validated_data['user_id'])
        follower_user = request.user

        try:
            follow_request = FollowRequest.objects.create(following=following_user, follower=follower_user)
        except IntegrityError:
            raise serializers.ValidationError(
                f"Request already exists from {follower_user.username} to {following_user.username}")

        return follow_request


class PendingFollowRequestsSerializer(ModelSerializer):
    follower = UserSocialDataSerializer(read_only=True)
    request_id = serializers.ReadOnlyField(source='id')

    class Meta:
        model = FollowRequest
        fields = ['request_id', 'follower', 'created_at']


class CommentDataSerializer(ModelSerializer):
    comment_id = serializers.ReadOnlyField(source='id')
    comment_by = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ['comment_id', 'content', 'comment_by', 'comment_by_id']


class CreatedBySerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_image']


class LikeDataSerializer(ModelSerializer):
    like_id = serializers.ReadOnlyField(source='id')
    liked_by = CreatedBySerializer()

    class Meta:
        model = Like
        fields = ['like_id', 'liked_by']


class PostDataSerializer(ModelSerializer):
    post_id = serializers.ReadOnlyField(source='id')
    comments = CommentDataSerializer(many=True, read_only=True)
    likes = LikeDataSerializer(many=True, read_only=True)
    comment_count = serializers.ReadOnlyField(source='comment_counts')
    like_count = serializers.ReadOnlyField(source='like_counts')
    restaurant = serializers.ReadOnlyField(source='restaurant.name')
    user = CreatedBySerializer()
    liked_by_you = SerializerMethodField('get_liked_by_you', read_only=True)

    def get_liked_by_you(self, obj):
        try:
            Like.objects.get(liked_by=self.context['request'].user, post=obj)
            return True
        except:
            return False

    class Meta:
        model = Post
        fields = ['post_id', 'user', 'restaurant', 'post_image', 'content', 'comment_count', 'like_count', 'comments', 'likes', 'liked_by_you']


class AddPostSerializer(ModelSerializer):
    restaurant_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Post
        fields = ['restaurant_id', 'post_image', 'content', 'latitude', 'longitude']

    def validate_restaurant_id(self, value):
        try:
            return Restaurant.objects.get(id=value)
        except Restaurant.DoesNotExist:
            return None

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['restaurant'] = validated_data.pop('restaurant_id')
        post = Post(user=user, **validated_data)
        post.save()

        return post


# ----------- EVENT -----------
class AddEventSerializer(ModelSerializer):
    restaurant = serializers.IntegerField(write_only=True, required=False)

    def validate_restaurant(self, value):
        try:
            return Restaurant.objects.get(id=value)
        except Restaurant.DoesNotExist:
            raise serializers.ValidationError({"details": f"Restaurant does not exist!"})

    class Meta:
        model = Event
        fields = ['restaurant', 'name', 'description', 'event_image', 'date_time']

    def create(self, validated_data):
        user = self.context.get('request').user
        event = Event(created_by=user, **validated_data)
        event.save()
        return event

    def validate(self, data):
        fields = ['restaurant', 'name', 'description', 'event_image', 'date_time']
        for field in fields:
            if field not in data:
                raise serializers.ValidationError({"details": f"{field} is required"})
            elif data[field] is None:
                raise serializers.ValidationError({"details": f"{field} cannot be null!"})

        return data


class EventRestaurantSerializer(ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['name', 'location']


class EventDataSerializer(ModelSerializer):
    event_id = serializers.ReadOnlyField(source='id')
    participant_counts = serializers.ReadOnlyField(source='participants_counts')
    restaurant = EventRestaurantSerializer()
    created_by = CreatedBySerializer()

    class Meta:
        model = Event
        fields = ['event_id', 'name', 'restaurant', 'participant_counts', 'description', 'event_image',
                  'date_time', 'created_by']


# ----------- User Profile -----------
class UserSocialMediaProfileSerializer(ModelSerializer):
    following_count = serializers.ReadOnlyField()
    follower_count = serializers.ReadOnlyField()
    request_count = serializers.ReadOnlyField()
    followings = serializers.SerializerMethodField(read_only=True)
    followers = serializers.SerializerMethodField(read_only=True)
    posts = PostDataSerializer(read_only=True, many=True)
    events_created = serializers.SerializerMethodField(read_only=True)
    events_participated = serializers.SerializerMethodField(read_only=True)

    def get_followings(self, obj):
        followings = FollowRequest.objects.filter(follower=obj, is_approved=True)
        return FollowingDataSerializer(followings, many=True).data

    def get_followers(self, obj):
        followers = FollowRequest.objects.filter(following=obj, is_approved=True)
        return FollowerDataSerializer(followers, many=True).data

    def get_events_created(self, obj):
        events = Event.objects.filter(created_by=obj)
        return EventDataSerializer(events, many=True).data

    def get_events_participated(self, obj):
        events = Event.objects.filter(participants__participated_by=obj)
        return EventDataSerializer(events, many=True).data

    class Meta:
        model = User
        fields = ['id', 'username', 'profile_image', 'bio', 'following_count', 'follower_count', 'request_count',
                  'followings', 'followers', 'posts', 'events_created', 'events_participated']


class AddCommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'content',
        ]

    def create(self, validated_data):
        user = self.context.get('request').user
        post = self.context.get('post')
        comment = Comment(comment_by=user, post=post, **validated_data)
        comment.save()
        return comment


class UserSocialDetailsSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'profile_image', 'following_count', 'follower_count', 'bio']


class UserReviewListSerializer(ModelSerializer):
    restaurant = ReviewRestaurantSerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'restaurant', 'rating', 'comment'
        ]
