from django.shortcuts import render
from rest_framework import viewsets
from cwfapi.models import Group, Event
from cwfapi.serializers import GroupSerializer, EventSerializer

class GroupViewset(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class EventViewset(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
