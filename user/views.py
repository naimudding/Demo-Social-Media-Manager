from django.http import JsonResponse
from django.db.utils import IntegrityError
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, pagination, status
from typing import Any, Dict
from django.db.models.query import QuerySet 

from .models import UserFriendMapper, User

from .serializers import UserSignUpSerializer, \
                        LoginSerializer, \
                        UserFriendMapperSerializer, \
                        AcceptRejectRequestSerializer, \
                        ListPendingRequestSerializer, \
                        ListFriendsSerializer
from .utils import ResponseHandler

User = get_user_model()

class DefaultPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'size'
    max_page_size = 10

class SignUpAPIView(APIView):
    serializer_class: Any = UserSignUpSerializer

    def post(self, request) -> JsonResponse:
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            User.objects.create_user(**serializer.validated_data)
            return JsonResponse({"message": "User created successfully.", "data": dict()}, status=status.HTTP_201_CREATED)
        resp: Dict[str, Any] = ResponseHandler.handle_error_response(serializer.errors)
        return JsonResponse(resp, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    serializer_class: Any = LoginSerializer

    def post(self, request) -> JsonResponse:
        serializer: Any = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email: str = request.data.get('email')
            password: str = request.data.get('password')
            user = authenticate(email=email.lower(), password=password)
            if not user:
                return JsonResponse({'message': 'Invalid credentials'}, 
                                    status=status.HTTP_401_UNAUTHORIZED)
            token, exp = user.generate_access_token()
            return JsonResponse({'message': 'Login successful',
                                 'access_token': token,
                                 'exp_in': int(exp.timestamp()),
                                 }, 
                                status = status.HTTP_200_OK)
        resp: Dict[str, Any] = ResponseHandler.handle_error_response(serializer.errors)
        return JsonResponse(resp, status=status.HTTP_400_BAD_REQUEST)
    
class UserSearchAPIView(generics.ListAPIView):
    permission_classes: tuple = (IsAuthenticated,)
    serializer_class: Any = UserSignUpSerializer
    pagination_class: Any = DefaultPagination

    def get_queryset(self) -> QuerySet: 
        queryset: QuerySet = User.objects.none()
        search_query: str = self.request.query_params.get('search', None)
        if search_query:
            # Check if search query is an email
            
            queryset = User.objects.filter(email=search_query)
            if not queryset.exists():
                # Search by name
                queryset = User.objects.filter(fullname__icontains=search_query)
        return queryset

    def list(self, request, *args, **kwargs) -> JsonResponse:
        queryset: QuerySet = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer_class()(page, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return JsonResponse({"results":serializer.data}, status=status.HTTP_200_OK)
    

class SendFriendRequestAPIView(generics.CreateAPIView):
    permission_classes: tuple = (IsAuthenticated,)
    queryset: Any = UserFriendMapper.objects.all()
    serializer_class: Any = UserFriendMapperSerializer

    def create(self, request, *args, **kwargs) -> JsonResponse:
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                if serializer.validated_data.get("friend")== request.user:
                    return JsonResponse({"message": "Cannot send request to self.", "data": dict()}, status=status.HTTP_400_BAD_REQUEST)
                serializer.save(user=request.user, status="pending")
            except IntegrityError:
                return JsonResponse({"message": "request already sent.", "data": dict()}, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse({"message": "request sent.", "data": dict()}, status=status.HTTP_201_CREATED)
        resp: Dict[str, Any] = ResponseHandler.handle_error_response(serializer.errors)
        return JsonResponse(resp, status=status.HTTP_400_BAD_REQUEST)

class AcceptRejectFriendRequestAPIView(APIView):
    permission_classes: tuple = (IsAuthenticated,)
    serializer_class: Any = AcceptRejectRequestSerializer


    def post(self, request, *args, **kwargs) -> JsonResponse:
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            action_status: str = serializer.validated_data.get('action')
            user: User = serializer.validated_data.get('user')
            try:
                instance: UserFriendMapper = UserFriendMapper.objects.get(user=user, friend=request.user, status="pending")
            except UserFriendMapper.DoesNotExist:
                return JsonResponse({"message": "No pending request from this user", "data": dict()}, 
                                    status=status.HTTP_404_NOT_FOUND)
            else:
                instance.status = action_status
                instance.save()
                # if action is accepted then creating a mutual friend mapper
                if action_status == "accepted":
                    user_frnd_map, is_created = UserFriendMapper.objects.get_or_create(
                        user=request.user, friend=user,
                        defaults={"status": "accepted"}
                    )
                    if not is_created:
                        user_frnd_map.update(status="accepted") 

                return JsonResponse({"message": "success", "data": dict()}, 
                                    status=status.HTTP_200_OK)
        resp: Dict[str, Any] = ResponseHandler.handle_error_response(serializer.errors)
        return JsonResponse(resp, status=status.HTTP_400_BAD_REQUEST)
    
class ListFriendsAPIView(generics.ListAPIView):
    permission_classes: tuple = (IsAuthenticated,)
    serializer_class: Any = ListFriendsSerializer
    pagination_class: Any = DefaultPagination

    def get_queryset(self):
        return UserFriendMapper.objects.filter(user=self.request.user, status="accepted")
    
    def list(self, request, *args, **kwargs) -> JsonResponse:
        queryset: QuerySet = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer_class()(page, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return JsonResponse({"results":serializer.data}, status=status.HTTP_200_OK)

class ListPendingRequestsAPIView(generics.ListAPIView):
    permission_classes: tuple = (IsAuthenticated,)
    serializer_class: Any = ListPendingRequestSerializer
    pagination_class: Any = DefaultPagination

    def get_queryset(self) -> QuerySet:
        return UserFriendMapper.objects.filter(friend=self.request.user, status="pending")
    
    def list(self, request, *args, **kwargs) -> JsonResponse:
        queryset: QuerySet = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer_class()(page, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return JsonResponse({"results":serializer.data}, status=status.HTTP_200_OK)
