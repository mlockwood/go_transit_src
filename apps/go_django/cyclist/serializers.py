from rest_framework import serializers

from . import models


class CyclistSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'first_name',
            'last_name',
            'phone',
            'email',
            'waiver',
            'waiver_time',
        )
        model = models.Cyclist


class CheckInOutSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'fleet',
            'bike',
            'duration',
            'check_out',
            'check_in'
        )
        model = models.CheckInOut
