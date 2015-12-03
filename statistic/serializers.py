from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from statistic.models import WordFrequency

class WordFrequencySerializer(ModelSerializer):
    text = serializers.CharField(source='word', max_length=400)
    size = serializers.IntegerField(source='frequency')

    class Meta:
        model = WordFrequency
        fields = ('text','size')