from django.urls import path
from . import views

urlpatterns = [
    path('get-todays-data/', views.get_todays_data, name='get_todays_data'),
    path('create-new-habit/', views.create_new_habit, name='create_new_habit'),
    path('edit-habit/<int:habit_id>/', views.edit_habit, name='edit_habit'),
    path('delete-habit/<int:habit_id>/', views.delete_habit, name='delete_habit'),
]
