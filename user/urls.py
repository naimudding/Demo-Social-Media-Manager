
from django.urls import path

from .views import *

urlpatterns = [
    path("signup", SignUpAPIView.as_view(), name = "signup"),
    path("login", LoginAPIView.as_view(), name = "login"),
    path("search", UserSearchAPIView.as_view(), name = "search_users"),
    path("send_request", SendFriendRequestAPIView.as_view(), name = "send_request"),
    path("action", AcceptRejectFriendRequestAPIView.as_view(), name = "send_request"),
    path("friends", ListFriendsAPIView.as_view(), name = "friends"),
    path("pending_requests", ListPendingRequestsAPIView.as_view(), name = "pending_requests")
]