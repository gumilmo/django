from .models import AnyShoes
from rest_framework import serializers

class StringSerializer(serializers.StringRelatedField):

    def to_internal_value(self, value):
        return value

class AnyShoesSerializer(serializers.ModelSerializer):

    category = StringSerializer(many=False)
    season = StringSerializer(many=False)
    gender = StringSerializer(many=False)

    class Meta:
        model = AnyShoes
        fields = ('__all__')


