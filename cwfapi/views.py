from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from cwfapi.models import Group, Event, UserProfile, Member, Comment, Bet
from cwfapi.serializers import GroupSerializer, GroupFullSerializer, UserProfileSerializer, UserSerializer, EventSerializer, ChangePasswordSerializer, MemberSerializer, CommentSerializer, EventFullSerializer, BetSerializer
from datetime import datetime
import pytz
import requests
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from django.contrib.auth.models import User

class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    @action(methods=['PUT'], detail=True, serializer_class=ChangePasswordSerializer, permission_classes=[IsAuthenticated])
    def change_password(self, request, pk):
        user = User.objects.get(pk=pk)
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            if not user.check_password(serializer.data.get('old_password')):
                return Response({'message': 'Password is incorrect'}, status = 400)
            user.set_password(serializer.data.get('new_password'))
            user.save()
            return Response({'message': 'Password updated'}, status = 200)


class CommentViewset(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class UserProfileViewset(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

class GroupViewset(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = GroupFullSerializer(instance, many=False, context={'request': request})
        return Response(serializer.data)

class EventViewset(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = EventFullSerializer(instance, many=False, context={'request': request})
        return Response(serializer.data)

    @action(methods=['PUT'], detail=True)
    def set_result(self, request, pk):
        event = self.get_object()

        price_end = self.fetch_price_end_from_coingecko(event)
        if price_end is not None:
            event.price_end = price_end
            event.save()
            self.calculate_points()
            serializer = EventFullSerializer(event, context={'request': request})
            return Response(serializer.data, status=200)
        else:
            response = {'message': "Unable to fetch price_end from CoinGecko"}
            return Response(response, status=400)

    def calculate_points(self):
        event = self.get_object()
        bets = event.bets.all()
        for bet in bets:
            user_points = 0

            # 10 pts for exact match
            if bet.price_end == event.price_end:
                user_points = 10
            else:
                # Calculate the percentage difference
                diff = abs(event.price_end - bet.price_end)
                percent_diff = (diff / event.price_end) * 100

                # 3 pts for within five percent
                if percent_diff <= 5:
                    user_points = 3
                # 1 pt for within ten percent
                elif percent_diff <= 10:
                    user_points = 1

            # Update user_points for the bet
            bet.points = user_points
            bet.save()

    def fetch_price_end_from_coingecko(self, event):
        coin_id = event.crypto.lower()
        end_time = event.end_time.strftime("%d-%m-%Y")
        url = f'https://api.coingecko.com/api/v3/coins/{coin_id}/history?date={end_time}&localization=false'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            price_usd = data.get('market_data', {}).get('current_price', {}).get('usd')
            return price_usd
        else:
            return None



class MemberViewset(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    @action(methods=['POST'], detail=False)
    def join(self, request):
        if 'group' in request.data and 'user' in request.data:
            try:
                group = Group.objects.get(id=request.data['group'])
                user = User.objects.get(id=request.data['user'])

                member = Member.objects.create(group=group, user=user, admin=False)
                serializer = MemberSerializer(member, many=False)
                response = {'message': 'Joined group', 'results': serializer.data}
                return Response(response, status=200)

            except:
                response = {'message': 'Cannot join'}
                return Response(response, status=400)
        else:
            response = {'message': 'Incorrect params'}
            return Response(response, status=400)

    @action(methods=['POST'], detail=False)
    def leave(self, request):
        if 'group' in request.data and 'user' in request.data:
            try:
                group = Group.objects.get(id=request.data['group'])
                user = User.objects.get(id=request.data['user'])

                member = Member.objects.get(group=group, user=user)
                member.delete()
                response = {'message': 'Left group'}
                return Response(response, status=200)

            except:
                response = {'message': 'Cannot leave group'}
                return Response(response, status=400)
        else:
            response = {'message': 'Incorrect params'}
            return Response(response, status=400)

class BetViewset(viewsets.ModelViewSet):
    queryset = Bet.objects.all()
    serializer_class = BetSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        response = {"message": "Method not allowed"}
        return Response(response, status=405)

    def update(self, request, *args, **kwargs):
        response = {"message": "Method not allowed"}
        return Response(response, status=405)

    @action(methods=['POST'], detail=False, url_path='place_bet')
    def place_bet(self, request):
        if 'event' in request.data and 'price_end' in request.data:
            event_id = request.data['event']
            event = Event.objects.get(id=event_id)

            in_group = self.checkIfUserInGroup(event, request.user)

            if event.end_time > datetime.now(pytz.UTC) and in_group:

                price_end = request.data['price_end']

                try:
                    #Attempted Update
                    my_bet = Bet.objects.get(event=event_id, user=request.user.id)
                    response = {"message": "Bet cannot be changed"}
                    return Response(response, status=400)
                except:
                    #Create bet
                    my_bet = Bet.objects.create(event=event, user=request.user, price_end=price_end)
                    serializer = BetSerializer(my_bet, many=False)
                    response = {"message": "Bet Created", "new": True, "result": serializer.data}
                    return Response(response, status=200)

            else:
                response = {"message": "Event is over. Can't place bet."}
                return Response(response, status=400)
        else:
            response = {"message": "Incorrect parameters"}
            return Response(response, status=400)

    def checkIfUserInGroup(self, event, user):
        try:
            return Member.objects.get(user=user, group=event.group)
        except:
            return False

class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user = User.objects.get(id=token.user_id)
        user_serializer = UserSerializer(user, many=False)
        return Response({'token': token.key, 'user': user_serializer.data})
