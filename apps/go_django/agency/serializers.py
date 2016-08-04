from rest_framework import serializers

from . import models


class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'lang',
            'name',
            'phone',
            'timezone',
            'url',
        )
        model = models.Agency
