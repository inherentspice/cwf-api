from rest_framework import serializers
from cwfapi.models import Group, Event, UserProfile
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('image',)

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    class Meta:
        model = User
        fields = ('id', 'username')

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'crypto', 'time', 'end_time', 'price_start', 'price_end', 'group')

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', 'location', 'description')

class GroupFullSerializer(serializers.ModelSerializer):
    events = EventSerializer(many=True)
    class Meta:
        model = Group
        fields = ('id', 'name', 'location', 'description', 'events')
