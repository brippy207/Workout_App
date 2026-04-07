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
    path('log-workout/', views.log_workout, name='log_workout'),
    path('log-weight/', views.log_weight, name='log_weight'),
    path('log-food/', views.log_food, name='log_food'),
    path('api/search-food/', views.api_food_search, name='api_search_food'),
]