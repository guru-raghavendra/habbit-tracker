from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import UserSerializer

class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer

@api_view(['POST'])
def login_view(request):
    # import pdb; pdb.set_trace()
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_401_UNAUTHORIZED)
