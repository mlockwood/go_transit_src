from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from . import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            'id',
            'username',
            'password',
            'email',
            'groups',
            'first_name',
            'last_name',
            'is_active',
            'is_staff'
        )
        write_only_fields = ('password',)

    # def create(self, validated_data):
    #     user = User.objects.create_user(
    #         username=validated_data['username'],
    #         email=validated_data['email'],
    #         groups=validated_data['groups'],
    #         first_name=validated_data['first_name'],
    #         last_name=validated_data['last_name'],
    #         is_active=validated_data['is_active'],
    #         is_staff=validated_data['is_staff'],
    #     )
    #     user.set_password(validated_data['password'])
    #     user.save()
    #     return user
    #
    # def create(self, validated_data):
    #     password = validated_data.pop('password', None)
    #     instance = self.Meta.model(**validated_data)
    #     if password is not None:
    #         instance.set_password(password)
    #     instance.save()
    #     return instance
    #
    # def update(self, instance, validated_data):
    #     for attr, value in validated_data.items():
    #         if attr == 'password':
    #             instance.set_password(value)
    #         else:
    #             setattr(instance, attr, value)
    #     instance.save()
    #     return instance


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
            'title_or_rank',
            'organization',
            'office_phone',
            'cell_phone',
            'mailing_address',
            'role_description',
            'waiver',
            'waiver_time',
            'status'
            'fleet',
        )
        model = models.EndUser


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'name',
            'description'
        )
        model = models.Organization
