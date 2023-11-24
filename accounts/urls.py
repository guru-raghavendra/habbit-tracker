from django.urls import path
from .views import CreateUserView, login_view

urlpatterns = [
    path('signup/', CreateUserView.as_view(), name='signup'),
    path('login/', login_view, name='login'),
]
