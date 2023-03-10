from django.shortcuts import render
from rest_framework import viewsets
from cwfapi.models import Group
from cwfapi.serializers import GroupSerializer

class GroupViewset(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
