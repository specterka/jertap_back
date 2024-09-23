from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from django.db.models import Q
from django.utils import timezone

from core.models import Review
from social.models import FollowRequest, Post, Comment, Like, Event, Participant
from social.serializers import (UserSocialMediaProfileSerializer, PendingFollowRequestsSerializer, AddPostSerializer,
                                SendFollowRequestSerializer, EditUserSocialProfileSerializer, SearchUserSerializer,
                                AddEventSerializer, EventDataSerializer, PostDataSerializer, AddCommentSerializer, UserSocialDetailsSerializer, UserReviewListSerializer)

from users.models import User
from users.permissions import IsVisitor

from owner_dashboard.views import CustomPagination


class SearchUserView(ListAPIView):
    permission_classes = [IsVisitor, ]
    serializer_class = SearchUserSerializer

    def get_queryset(self):
        search_user = self.request.query_params.get('search')
        queryset = User.objects.filter(is_visitor=True).exclude(id=self.request.user.id).order_by('email')
        if search_user:
            return queryset.filter(Q(username__istartswith=search_user) | Q(email__istartswith=search_user)).distinct()[:20]
        return queryset[:20]


class EditUserSocialProfileView(UpdateAPIView):
    permission_classes = [IsVisitor, ]
    serializer_class = EditUserSocialProfileSerializer

    def get_object(self):
        return User.objects.get(id=self.request.user.id)

    def put(self, request, *args, **kwargs):
        return Response({'detail': 'method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"detail": "User profile updated successfully."}, status=status.HTTP_200_OK)


class UserSocialMediaProfileView(RetrieveAPIView):
    serializer_class = UserSocialMediaProfileSerializer
    permission_classes = [IsVisitor, ]
    lookup_field = 'id'

    def get_object(self):
        try:
            return User.objects.get(id=self.kwargs.get('id'))
        except User.DoesNotExist:
            raise NotFound(f"User does not exists.")


class SendFollowRequestView(CreateAPIView):
    serializer_class = SendFollowRequestSerializer
    permission_classes = [IsVisitor, ]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"detail": f"Follow Request sent successfully."}, status=status.HTTP_201_CREATED)


class PendingFollowRequestsView(ListAPIView):
    serializer_class = PendingFollowRequestsSerializer
    permission_classes = [IsVisitor, ]
    pagination_class = CustomPagination

    def get_queryset(self):
        return FollowRequest.objects.filter(following=self.request.user, is_approved=False).order_by('-created_at')


class AcceptFollowRequestView(APIView):
    permission_classes = [IsVisitor, ]
    lookup_field = 'id'

    def get_object(self):
        try:
            obj = FollowRequest.objects.get(id=self.kwargs.get(self.lookup_field))
            return obj
        except FollowRequest.DoesNotExist:
            raise NotFound(f"Follow request does not exists.")

    def put(self, request, *args, **kwargs):
        return Response({'detail': 'method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.is_approved = True
        obj.save()
        return Response({"detail": "Follow request accepted successfully."}, status=status.HTTP_200_OK)


class DeleteFollowRequestOrFollowerView(DestroyAPIView):
    permission_classes = [IsVisitor, ]
    lookup_field = 'id'

    def get_queryset(self):
        return FollowRequest.objects.filter(following=self.request.user)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        return Response({"detail": "Follow request deleted or removed follower successfully."},
                        status=status.HTTP_200_OK)


class UnfollowUserView(DestroyAPIView):
    permission_classes = [IsVisitor, ]
    lookup_field = 'id'

    def get_queryset(self):
        return FollowRequest.objects.filter(follower=self.request.user)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        return Response({"detail": "Unfollowed successfully."}, status=status.HTTP_200_OK)


# ---------- POST ----------
class AddPostView(CreateAPIView):
    permission_classes = [IsVisitor, ]
    serializer_class = AddPostSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"detail": "Post created  successfully."}, status=status.HTTP_201_CREATED)


class DeletePostView(DestroyAPIView):
    permission_classes = [IsVisitor, ]
    lookup_field = 'id'

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        return Response({"detail": "Post deleted successfully."}, status=status.HTTP_200_OK)


class AllUpdatesView(ListAPIView):
    permission_classes = [IsVisitor, ]
    serializer_class = PostDataSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        following = User.objects.filter(user_following__follower=self.request.user)
        return Post.objects.filter(user__in=following).order_by('-created_at')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        try:
            user = self.request.user
        except:
            user = None
        context.update({"user": user})
        return context


# ---------- COMMENT ----------
class AddCommentView(CreateAPIView):
    permission_classes = [IsVisitor, ]
    serializer_class = AddCommentSerializer

    def post(self, request, *args, **kwargs):
        post_id = self.kwargs.get('post_id')
        try:
            post = Post.objects.get(id=post_id)
        except:
            return Response({"detail": 'Post not found.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data, context={'request': request, 'post': post})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"detail": "Comment added successfully.", 'comment_counts': post.comment_counts}, status=status.HTTP_201_CREATED)


class DeleteCommentView(DestroyAPIView):
    permission_classes = [IsVisitor, ]
    lookup_field = 'id'

    def get_queryset(self):
        return Comment.objects.filter((Q(comment_by=self.request.user) | Q(post__user=self.request.user)))

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        return Response({"detail": "Comment deleted successfully"}, status=status.HTTP_200_OK)


# ---------- LIKE ----------
class LikePostView(APIView):
    permission_classes = [IsVisitor, ]

    def post(self, request, *args, **kwargs):
        post_id = self.kwargs.get('post_id')
        try:
            post = Post.objects.get(id=post_id)
            user = self.request.user
            like_obj, created = Like.objects.get_or_create(liked_by=user, post=post)
            if not created:
                like_obj.delete()
                return Response({'detail': 'Like removed successfully.', 'like_counts': post.like_counts}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Liked successfully.', 'like_counts': post.like_counts}, status=status.HTTP_201_CREATED)
        except:
            return Response({'detail': 'Post not found.'}, status=status.HTTP_400_BAD_REQUEST)


class AddEventView(CreateAPIView):
    permission_classes = [IsVisitor, ]
    serializer_class = AddEventSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"detail": "Event created  successfully."}, status=status.HTTP_201_CREATED)


class DeleteEventView(DestroyAPIView):
    permission_classes = [IsVisitor, ]
    lookup_field = 'id'

    def get_queryset(self):
        return Event.objects.filter(created_by=self.request.user)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        return Response({"detail": "Event deleted successfully."}, status=status.HTTP_200_OK)


class EventParticipateView(APIView):
    permission_classes = [IsVisitor, ]

    def post(self, request, *args, **kwargs):
        event_id = self.kwargs.get('event_id')
        try:
            event = Event.objects.get(id=event_id, is_approved_by_restaurant=True)
            user = self.request.user
            participant_obj, created = Participant.objects.get_or_create(event=event, participated_by=user)
            if not created:
                participant_obj.delete()
                return Response({'detail': 'Refrain successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Participated successfully.'}, status=status.HTTP_201_CREATED)
        except:
            return Response({'detail': 'Event not found.'}, status=status.HTTP_400_BAD_REQUEST)


class UpcomingEventsView(ListAPIView):
    serializer_class = EventDataSerializer
    permission_classes = [IsVisitor, ]
    pagination_class = CustomPagination

    def get_queryset(self):
        now = timezone.now()
        return Event.objects.filter(date_time__gt=now, is_approved_by_restaurant=True)


class AllEventsView(ListAPIView):
    serializer_class = EventDataSerializer
    permission_classes = [IsVisitor, ]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Event.objects.filter(is_approved_by_restaurant=True)


class UserSocialDetails(RetrieveAPIView):
    serializer_class = UserSocialDetailsSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return User.objects.filter(is_visitor=True)


class UserReviewList(ListAPIView):
    serializer_class = UserReviewListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Review.objects.filter(user__id=user_id).order_by('-id')


class UserPostList(ListAPIView):
    serializer_class = PostDataSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Post.objects.filter(user__id=user_id).order_by('-id')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        try:
            user = self.request.user
        except:
            user = None
        context.update({"user": user})
        return context