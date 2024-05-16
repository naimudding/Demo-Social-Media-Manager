from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserFriendMapper

User = get_user_model()

class UserSignUpSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'password', 'confirm_password', 'mobile']
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
        }

    def validate_password(self, value):
        if not any(char.isdigit() for char in value) or not any(char.isalpha() for char in value):
            raise serializers.ValidationError("Password should contain at least one letter and one digit.")
        return value
        
    def validate(self, data):
        confirm_password = data.pop('confirm_password')
        if data.get('password') != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")
        return data

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class UserFriendMapperSerializer(serializers.ModelSerializer):
    friend = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = UserFriendMapper
        fields = ['id', 'user', 'friend', 'status']
        read_only_fields = ['id', 'user', 'status']


class AcceptRejectRequestSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    action = serializers.CharField(max_length=10)

    class Meta:
        model = UserFriendMapper
        fields = ['user', 'action']

    def validate_action(self, value):
        if value not in ["accepted", "rejected"]:
            raise serializers.ValidationError("Invalid action")
        return value

class ListFriendsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="friend.id")
    first_name = serializers.CharField(source="friend.first_name")
    last_name = serializers.CharField(source="friend.last_name")
    email = serializers.CharField(source="friend.email")
    mobile = serializers.CharField(source="friend.mobile")

    class Meta:
        model = UserFriendMapper
        fields = ["id", "first_name", "last_name", "email", "mobile"]

class ListPendingRequestSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.CharField(source="user.email")
    mobile = serializers.CharField(source="user.mobile")

    class Meta:
        model = UserFriendMapper
        fields = ["id", "first_name", "last_name", "email", "mobile"]