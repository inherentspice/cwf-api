from django.contrib import admin
from .models import Group, Event, UserProfile, Member

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    fields = ('name', 'location', 'description')
    list_display = ('id', 'name', 'location', 'description')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    fields = ('user', 'image', 'bio')
    list_display = ('id', 'user', 'image', 'bio')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    fields = ('crypto', 'time', 'end_time', 'price_start', 'price_end', 'group')
    list_display = ('id', 'crypto', 'time', 'end_time', 'price_start', 'price_end', 'group')

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    fields = ('user', 'group', 'admin')
    list_display = ('id', 'user', 'group', 'admin')
