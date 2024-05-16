from django.contrib import admin
from user.models import User, UserFriendMapper

class UserAdmin(admin.ModelAdmin):
    list_display = ["first_name", "email", "last_login"]

class UserFriendMapperAdmin(admin.ModelAdmin):
    list_display = ["user", "friend", "status"]

admin.site.register(User, UserAdmin)

admin.site.register(UserFriendMapper, UserFriendMapperAdmin)
