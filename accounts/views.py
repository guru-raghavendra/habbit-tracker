from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from dashboard.models import HabitStats
from .serializers import UserSerializer
from django.utils import timezone
from datetime import timedelta



class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    
    def perform_create(self, serializer):
        user = serializer.save()

        end_date = timezone.localtime(timezone.now()).date()
        start_date = end_date - timedelta(days=30)

        habit_stats_objects = [
            HabitStats(user=user, date=start_date + timedelta(days=day), total_habits=0, completed_habits=0)
            for day in range(31)
        ]

        HabitStats.objects.bulk_create(habit_stats_objects)

@api_view(['POST'])
def login_view(request):
    # import pdb; pdb.set_trace()
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
    return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
