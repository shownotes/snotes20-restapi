from rest_framework import serializers
from statistic.models import WordFrequency

class WordFrequencySerializer(serializers.ModelSerializer):
    word = serializers.CharField(source='word', max_length=400)
    frequency = serializers.IntegerField(source='frequency')

    class Meta:
        model = WordFrequency
        fields = ('word','frequency')

class WordListSerializer(serializers.ModelSerializer):
    word = serializers.CharField(max_length=400)

    class Meta:
        model = WordFrequency
        fields = ('word',)

    def to_native(self, obj):
        print(obj['word'])
        return obj['word']

