from rest_framework import serializers
from cwfapi.models import Group, Event

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', 'location', 'description')

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'crypto', 'time', 'price_start', 'price_end', 'group')
