from rest_framework import serializers
from .models import Habit, HabitLog, HabitStats

class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = ['id', 'name', 'created_at', 'deleted_at']
        read_only_fields = ['created_at', 'deleted_at']

class HabitLogSerializer(serializers.ModelSerializer):
    habit_name = serializers.SerializerMethodField()
    class Meta:
        model = HabitLog
        fields = [ 'habit', 'habit_name', 'completed']
        read_only_fields = ['date']
        
    def get_habit_name(self, obj):
        return obj.habit.name
        

class HabitStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitStats
        fields = [ 'date', 'total_habits' , 'completed_habits']
        read_only_fields = ['date', ]
