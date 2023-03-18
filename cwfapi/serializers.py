from rest_framework import serializers
from cwfapi.models import Group, Event, UserProfile, Member, Comment, Bet
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'image', 'bio')

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'profile')
        extra_kwargs = {'password': {'write_only': True, 'required': False}}

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user, **profile_data)
        Token.objects.create(user=user)
        return user

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'crypto', 'time', 'price_start', 'end_time', 'group')

class BetSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    class Meta:
        model = Bet
        fields = ('id', 'user', 'event', 'price_end')

class EventFullSerializer(serializers.ModelSerializer):
    bets = BetSerializer(many=True)
    class Meta:
        model = Event
        fields = ('id', 'crypto', 'time', 'end_time', 'price_start', 'price_end', 'group', 'bets')

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('user', 'group', 'description', 'time')

class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    class Meta:
        model = Member
        fields = ('group', 'user', 'admin')

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', 'location', 'description')

class GroupFullSerializer(serializers.ModelSerializer):
    events = EventSerializer(many=True)
    members = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ('id', 'name', 'location', 'description', 'events', 'members', 'comments')

    def get_members(self, obj):
        people_points = []
        members = obj.members.all()
        for member in members:
            points = 0
            members_serialized = MemberSerializer(member, many=False)
            member_data = members_serialized.data
            member_data['points'] = points
            people_points.append(member_data)
        return people_points

    def get_comments(self, obj):
        comments = Comment.objects.filter(group=obj).order_by('-time')
        serializer = CommentSerializer(comments, many=True)
        return serializer.data
