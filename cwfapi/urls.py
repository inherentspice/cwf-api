from django.urls import path, include
from cwfapi import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'groups', views.GroupViewset)
urlpatterns = [
    path(r'^', include(router.urls)),
]
