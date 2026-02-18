from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('workouts/', views.workouts, name='workouts'),
    path('nutrition/', views.nutrition, name='nutrition'),
    # This <str:name> captures whatever is in the URL (e.g., /lifting/)
    path('workouts/<str:name>/', views.category_detail, name='category'),
]