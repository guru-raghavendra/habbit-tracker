from django.utils import timezone
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(max_length=255)
    created_at = models.DateField(auto_now_add=True)
    deleted_at = models.DateField(null=True, blank=True)
    
    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.save()

    def __str__(self):
        return self.name

class HabitLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField()
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('habit', 'date')

    def __str__(self):
        return f"{self.habit.name} on {self.date}: {'Completed' if self.completed else 'Not Completed'}"

class HabitStats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    total_habits = models.PositiveIntegerField(default=0)
    completed_habits = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"Stats for {self.user} on {self.date}"

    @property
    def completion_ratio(self):
        if self.total_habits > 0:
            return self.completed_habits / self.total_habits
        return -1
