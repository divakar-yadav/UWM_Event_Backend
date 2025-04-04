
from rest_framework import serializers
from .models import  ThreeMt
from signup.UserSerializer import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class ThreeMtSerializer(serializers.ModelSerializer):
    poster_id = serializers.IntegerField(read_only=True)  # Explicitly define poster_ID as primary key
    poster_title = serializers.CharField(source='student.poster_title', read_only=True)
    student_name = serializers.CharField(source='student.Name', read_only=True)

    class Meta:
        model = ThreeMt
        fields = '__all__'


class UpdateThreeMtSerializer(serializers.ModelSerializer):
    judge = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)  # Accept only user ID
    poster_id = serializers.IntegerField(read_only=True)  # Explicitly define poster_ID as primary key

    class Meta:
        model = ThreeMt
        fields = ['poster_id', 'judge', 'comprehension_content', 'engagement', 
                  'communication', 'overall_impression', 'feedback']

    def update(self, instance, validated_data):
        # Handle judge field separately if it's being updated
        if 'judge' in validated_data:
            instance.judge = validated_data.pop('judge')
        
        return super().update(instance, validated_data)
