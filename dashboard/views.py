from datetime import timedelta
import json
from django.utils import timezone
from calendar import monthrange
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import Habit, HabitLog, HabitStats
from .serializers import HabitSerializer, HabitLogSerializer, HabitStatsSerializer




def get_todays_habits(user):
    today = timezone.localtime(timezone.now()).date()
    habits = Habit.objects.filter(
        user=user, 
        deleted_at__isnull=True
    )
    habit_logs = HabitLog.objects.filter(habit__in=habits, date=today)

    # Ensuring each habit has a log for today
    for habit in habits:
        if not habit_logs.filter(habit=habit).exists():
            HabitLog.objects.create(habit=habit, date=today, completed=False)

    # Re-fetching to include newly created logs
    habit_logs = HabitLog.objects.filter(habit__in=habits, date=today)
    return HabitLogSerializer(habit_logs, many=True).data



def update_habit_stats(user, date):
    # Calculate total habits for the user that are not deleted
    active_habits = Habit.objects.filter(
        user=user, 
        created_at__lte=date,
        deleted_at__isnull=True
    )
    
    total_habits = active_habits.count()

    # Calculate completed habits for the user on the given date
    completed_habits = HabitLog.objects.filter(
        habit__in=active_habits,
        date=date,
        completed=True
    ).count()

    # Get or create a HabitStats object for the user on the given date
    habit_stats, created = HabitStats.objects.get_or_create(user=user, date=date)

    # Update the total and completed habit counts
    habit_stats.total_habits = total_habits
    habit_stats.completed_habits = completed_habits
    habit_stats.save()


def get_monthly_stats(user):
    end_date = timezone.localtime(timezone.now()).date()
    start_date = end_date - timedelta(days=30)
    
    update_habit_stats(user, end_date)
    
    monthly_stats = HabitStats.objects.filter(
        user=user, 
        date__range=(start_date, end_date)
    ).order_by('date')  # Sorting by date

    return HabitStatsSerializer(monthly_stats, many=True).data


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_todays_data(request):
    user = request.user

    todays_habits = get_todays_habits(user)
    month_stats = get_monthly_stats(user)

    data = {
        'todays_habits': todays_habits,
        'month_stats': month_stats
    }

    return Response(data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_new_habit(request):
    habit_name = request.data.get('name')
    if not habit_name:
        return Response(
            {'error': 'Habit name is required.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    user = request.user
    Habit.objects.create(user=user, name=habit_name)
    data = {
        'month_stats': get_monthly_stats(user),
        'todays_habits': get_todays_habits(user),
        'message': 'Success'
    }

    return Response(data, status=status.HTTP_200_OK)



@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def edit_habit(request, habit_id):
    new_habit_name = request.data.get('name')
    if not new_habit_name:
        return Response(
            {'error': 'New habit name is required.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    user = request.user
    try:
        habit = Habit.objects.get(id=habit_id, user=user)
        habit.name = new_habit_name
        habit.save()
    except Habit.DoesNotExist:
        return Response(
            {'error': 'Habit not found.'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    return Response({'message': 'Success'}, status=status.HTTP_200_OK)



@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_habit(request, habit_id):
    user = request.user
    try:
        habit = Habit.objects.get(id=habit_id, user=user)
    except Habit.DoesNotExist:
        return Response(
            {'error': 'Habit not found.'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    habit.deleted_at = timezone.localtime(timezone.now()).date()
    habit.save()
    data = {
        'month_stats': get_monthly_stats(user),
        'message': 'success'
    }

    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def save_habit_statuses(request):
    status_updates = request.data
    user = request.user
    today = timezone.localtime(timezone.now()).date()
    updated_habits = set()
    for update in status_updates:
        habit_id = update.get('habit_id')
        new_status = update.get('status')

        if habit_id is None or new_status is None:
            return Response(
                {'error': 'Invalid data. Each item must have habit_id and status.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            habit_log = HabitLog.objects.get(habit__id=habit_id, habit__user=user, date=today)
            habit_log.completed = new_status
            habit_log.save()
            updated_habits.add(habit_id)
        except HabitLog.DoesNotExist:
            pass

    if updated_habits:
        total_habits = Habit.objects.filter(user=user, deleted_at__isnull=True).count()
        completed_habits = HabitLog.objects.filter(
            habit__user=user, 
            date=today, 
            completed=True
        ).count()

        stats, created = HabitStats.objects.get_or_create(user=user, date=today)
        stats.total_habits = total_habits
        stats.completed_habits = completed_habits
        stats.save()

    return Response({'message': 'Habit statuses and stats updated successfully'}, status=status.HTTP_200_OK)
