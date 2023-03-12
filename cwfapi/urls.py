from django.urls import re_path, include
from cwfapi import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'groups', views.GroupViewset)
router.register(r'events', views.EventViewset)

urlpatterns = [
    re_path(r'^', include(router.urls)),
]
