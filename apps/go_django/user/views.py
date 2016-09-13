from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, permissions, status, viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

from . import models
from . import serializers


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_superuser and request.method == 'DELETE':
            return False
        return True


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    @list_route(methods=['get'], url_path='username/(?P<username>\w+)')
    def get_by_username(self, request, username):
        user = get_object_or_404(User, username=username)
        return Response(serializers.UserSerializer(user).data, status=status.HTTP_200_OK)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer


class EndUserViewSet(viewsets.ModelViewSet):
    queryset = models.EndUser.objects.all()
    serializer_class = serializers.EndUserSerializer
