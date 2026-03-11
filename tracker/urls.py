from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('stats/', views.stats, name='stats'),  
    path('workouts/', views.workouts, name='workouts'),
    path('nutrition/', views.nutrition, name='nutrition'),
    path('workouts/<str:name>/', views.category_detail, name='category'),
    path('workout/<str:workout_name>/', views.workout_setup, name='workout_setup'),
    path('signup/', views.signup, name='signup'),
]



