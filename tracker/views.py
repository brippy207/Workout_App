from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def home(request):
    return render(request, 'tracker/home.html')\

def workouts(request):
    return render(request, 'tracker/workouts.html')

def nutrition(request):
    return render(request, 'tracker/nutrition.html')

def category_detail(request, name):
    # Dictionary to hold your specific categories
    data = {
        'lifting': ['Chest', 'Back', 'Arms', 'Legs', 'Push', 'Pull', 'Upper', 'Full Body'],
        'cardio': ['Running', 'Rowing', 'Cycling', 'Swimming', 'HIIT', 'Stair Climber', 'Elliptical'],
        'sports': ['Basketball', 'Badminton', 'Baseball', 'Pickleball', 'Tennis', 'Volleyball'],
        'stretching': ['Yoga', 'Upper Body', 'Lower Body', 'Full Body Mobility', 'Dynamic Stretching', 'Static Stretching'],
    }
    
    context = {
        'category_name': name,
        'sub_categories': data.get(name, [])
    }
    return render(request, 'tracker/category_detail.html', context)

def workout_setup(request, workout_name):
    # This list will populate your 70s dropdown
    gym_options = [
        "No Equipment (Bodyweight)",
        "Home Gym / Dumbbells",
        "General Commercial Gym",
        "Planet Fitness",
        "Crunch Fitness",
        "Life Time Fitness"
    ]
    
    context = {
        'workout_name': workout_name,
        'gym_options': gym_options
    }
    return render(request, 'tracker/workout_setup.html', context)