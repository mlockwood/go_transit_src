from rest_framework import serializers

from . import models


class EndUserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'user',
            # 'first_name',
            # 'last_name',
            # 'rank',
            # 'phone',
            # 'email',
            'go_permission',
            'transit_staff',
            'fleet',
            'waiver',
            'waiver_time',
            'status'
        )
        model = models.EndUser

