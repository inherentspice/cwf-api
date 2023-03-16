from django.urls import re_path, include, path
from cwfapi import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'groups', views.GroupViewset)
router.register(r'events', views.EventViewset)
router.register(r'members', views.MemberViewset)
router.register(r'users', views.UserViewset)
router.register(r'profile', views.UserProfileViewset)


urlpatterns = [
    re_path(r'^', include(router.urls)),
    path('authenticate/', views.CustomObtainAuthToken.as_view()),
]
