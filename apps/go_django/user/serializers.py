from rest_framework import serializers

from . import models


class EndUserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'user',
            # 'first_name',
            # 'last_name',
            # 'rank',
            # 'phone',
            # 'email',
            'fleet',
            'waiver',
            'waiver_time',
            'status'
        )
        model = models.EndUser

