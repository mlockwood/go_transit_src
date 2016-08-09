from rest_framework import serializers
from django.contrib.auth.models import Group, User

from . import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'groups',
            'first_name',
            'last_name',
            'is_active',
            'is_staff'
            # 'rank',
            # 'phone',
        )


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = (
            'id',
            'name'
        )


class EndUserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'user',
            'fleet',
            'waiver',
            'waiver_time',
            'status'
        )
        model = models.EndUser

