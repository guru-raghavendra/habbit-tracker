from rest_framework import serializers
from .models import Habit, HabitLog, HabitStats

class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = ['id', 'name', 'created_at', 'deleted_at']
        read_only_fields = ['created_at', 'deleted_at']

class HabitLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitLog
        fields = ['id', 'habit', 'date', 'completed']
        read_only_fields = ['date']
        

class HabitStatsSerializer(serializers.ModelSerializer):
    completion_ratio = serializers.FloatField(read_only=True)

    class Meta:
        model = HabitStats
        fields = ['user', 'date', 'total_habits', 'completed_habits', 'completion_ratio']
        read_only_fields = ['date', 'total_habits', 'completed_habits', 'completion_ratio']
