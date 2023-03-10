from rest_framework import serializers
from cwfapi.models import Group

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model: Group
        fields = ('id', 'name', 'location', 'description')
