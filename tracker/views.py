from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm
from .models import WorkoutLog, WeightEntry, Profile
import json

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/tracker/')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})

@login_required
def home(request):
    return render(request, 'tracker/home.html')

@login_required
def workouts(request):
    return render(request, 'tracker/workouts.html')

@login_required
def nutrition(request):
    return render(request, 'tracker/nutrition.html')

@login_required
def category_detail(request, name):
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

@login_required
def workout_setup(request, workout_name):
    gym_options = [
        "No Equipment (Bodyweight)",
        "Home Gym / Dumbbells",
        "General Commercial Gym",
    ]
    return render(request, 'tracker/workout_setup.html', {'workout_name': workout_name, 'gym_options': gym_options})

@login_required
def log_workout(request):
    if request.method == 'POST':
        activity = request.POST.get('activity')
        dist = request.POST.get('distance')
        dur = request.POST.get('duration')
        
        # Color mapping for Google Calendar style colors
        color_map = {
            'Running': '#3498db', 'Swimming': '#2ecc71', 
            'Cycling': '#f1c40f', 'HIIT': '#e74c3c'
        }
        
        WorkoutLog.objects.create(
            user=request.user,
            activity_name=activity,
            distance=dist,
            duration=dur,
            color=color_map.get(activity, '#95a5a6')
        )
        return redirect('workouts')

@login_required
def stats(request):
    profile = Profile.objects.filter(user=request.user).first()
    workouts = WorkoutLog.objects.filter(user=request.user).order_by('date')
    weights = WeightEntry.objects.filter(user=request.user).order_by('date')

    events = []
    for workout in workouts:
        if workout.distance:
            title = f"{workout.activity_name} ({workout.distance} mi)"
        else:
            title = workout.activity_name

        events.append({
            'title': title,
            'start': workout.date.isoformat(),
            'color': workout.color,
        })

    labels = [entry.date.strftime("%m/%d") for entry in weights]
    values = [entry.weight for entry in weights]
    current_weight = values[-1] if values else getattr(profile, 'weight', None)

    context = {
        'profile': profile,
        'current_weight': current_weight,
        'events_json': json.dumps(events),
        'labels_json': json.dumps(labels),
        'values_json': json.dumps(values),
    }
    return render(request, 'tracker/stats.html', context)
