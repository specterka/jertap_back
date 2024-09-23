from django.urls import path

from social.views import (UserSocialMediaProfileView, SendFollowRequestView, SearchUserView, EventParticipateView,
                          PendingFollowRequestsView, AcceptFollowRequestView, DeleteFollowRequestOrFollowerView,
                          UnfollowUserView, AddPostView, DeletePostView, AddCommentView, AddEventView, DeleteEventView,
                          DeleteCommentView, LikePostView, EditUserSocialProfileView, UpcomingEventsView, AllEventsView,
                          AllUpdatesView, UserSocialDetails, UserReviewList, UserPostList)

app_name = 'social_features'
social_api_v1_urlpatterns = [

    path('search-user/', SearchUserView.as_view(), name='Search User By Username or Email'),
    path('profile/<int:id>/', UserSocialMediaProfileView.as_view(), name='User Social Media Profile'),
    path('edit-profile/', EditUserSocialProfileView.as_view(), name='Edit User Profile Image or Bio'),

    path('send-follow-request/', SendFollowRequestView.as_view(), name="Send Follow Request"),
    path('pending-follow-requests/', PendingFollowRequestsView.as_view(), name="Users all Follow Requests"),
    path('accept-follow-request/<int:id>/', AcceptFollowRequestView.as_view(), name="Accept Follow Request"),
    path('delete-follow-request-or-follower/<int:id>/', DeleteFollowRequestOrFollowerView.as_view(), name="Delete Follow Request or follower"),
    path('unfollow-user/<int:id>/', UnfollowUserView.as_view(), name="Revoke Follow Request or Unfollow user"),

    path('all-updates/', AllUpdatesView.as_view(), name="All updates"),
    path('add-post/', AddPostView.as_view(), name="Add post "),
    path('delete-post/<int:id>/', DeletePostView.as_view(), name="Delete post"),
    path('add-comment/<int:post_id>/', AddCommentView.as_view(), name="Add Comment"),
    path('delete-comment/<int:id>/', DeleteCommentView.as_view(), name="Delete Comment"),
    path('like-or-unlike-post/<int:post_id>/', LikePostView.as_view(), name="Like or Unlike Post"),

    path('add-event/', AddEventView.as_view(), name="Add Event"),
    path('delete-event/<int:id>/', DeleteEventView.as_view(), name="Delete Event"),
    path('participate-or-refrain-event/<int:event_id>/', EventParticipateView.as_view(), name="Participate or Unparticipate Event"),

    path('all-events/', AllEventsView.as_view(), name="All Events"),
    path('upcoming-events/', UpcomingEventsView.as_view(), name="Upcoming Events"),

    path('user-social-profile/<int:id>/', UserSocialDetails.as_view(), name="User Social Profile Details"),
    path('user-review-list/<int:user_id>/', UserReviewList.as_view(), name="User reviews"),
    path('user-post-list/<int:user_id>/', UserPostList.as_view(), name="User posts"),

]
