from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db import DatabaseError
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import FoodLog, UserGoal 

from .forms import SignUpForm
from .models import (
    WorkoutLog,
    WeightEntry,
    Profile,
    CustomLiftWorkout,
    CustomLiftExercise,
    LiftExerciseLog,
)

import json
import requests
import logging
from django.conf import settings


def _parse_positive_int(value):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None

    return parsed if parsed > 0 else None


def _parse_nonnegative_float(value):
    if value in (None, ""):
        return 0.0

    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None

    return parsed if parsed >= 0 else None


def _parse_optional_positive_float(value):
    if value in (None, ""):
        return None

    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None

    return parsed if parsed > 0 else None


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
    custom_workouts = CustomLiftWorkout.objects.filter(user=request.user)
    return render(request, 'tracker/workouts.html', {
        'custom_workouts': custom_workouts
    })


@login_required
def nutrition(request):
    # This finds the goal in the DB. If it's not there, it creates it.
    goal, created = UserGoal.objects.get_or_create(user=request.user)
    
    # If the user is new, 'created' will be True and goals will be 0.
    # Let's ensure they have real numbers if they are new:
    if created:
        goal.protein_goal = 150
        goal.carb_goal = 250
        goal.fat_goal = 70
        goal.save()

    return render(request, 'tracker/nutrition.html', {'goal': goal})

def nutrition_tracker(request):
    # 1. Get the data
    user_goal, created = UserGoal.objects.get_or_create(user=request.user)
    logs = FoodLog.objects.filter(user=request.user).order_by('-id')

    # 2. Put it in the box (context)
    context = {
        'goal': user_goal,  # This MUST match the 'goal' in {{ goal.protein_goal }}
        'food_logs': logs,
    }

    # 3. Send the box to the template
    return render(request, 'tracker/nutrition.html', context)

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
        'sub_categories': data.get(name, []),
    }

    if name == 'lifting':
        context['custom_workouts'] = CustomLiftWorkout.objects.filter(user=request.user)

    return render(request, 'tracker/category_detail.html', context)

@login_required
def workout_setup(request, workout_name):
    gym_options = [
        "No Equipment (Bodyweight)",
        "Home Gym / Dumbbells",
        "General Commercial Gym",
    ]

    custom_workouts = CustomLiftWorkout.objects.filter(user=request.user)

    return render(request, 'tracker/workout_setup.html', {
        'workout_name': workout_name,
        'gym_options': gym_options,
        'custom_workouts': custom_workouts,
    })

@login_required
def create_custom_workout(request):
    if request.method == 'POST':
        workout_name = (request.POST.get('workout_name') or '').strip()
        exercise_names = request.POST.getlist('exercise_name[]')
        sets_list = request.POST.getlist('sets[]')
        reps_list = request.POST.getlist('reps[]')
        weights_list = request.POST.getlist('weight[]')

        if not workout_name:
            messages.error(request, "Enter a workout name.")
            return redirect('create_custom_workout')

        workout = CustomLiftWorkout.objects.create(
            user=request.user,
            name=workout_name
        )

        for i, exercise_name in enumerate(exercise_names):
            exercise_name = (exercise_name or '').strip()
            sets_value = _parse_positive_int(sets_list[i]) if i < len(sets_list) else None
            reps_value = _parse_positive_int(reps_list[i]) if i < len(reps_list) else None
            weight_value = _parse_nonnegative_float(weights_list[i]) if i < len(weights_list) else None

            if exercise_name and sets_value and reps_value and weight_value is not None:
                CustomLiftExercise.objects.create(
                    workout=workout,
                    exercise_name=exercise_name,
                    default_sets=sets_value,
                    default_reps=reps_value,
                    default_weight=weight_value
                )

        messages.success(request, "Custom workout saved.")
        return redirect('custom_workout_detail', workout_id=workout.id)

    return render(request, 'tracker/custom_workout_builder.html')


@login_required
def custom_workout_detail(request, workout_id):
    workout = CustomLiftWorkout.objects.filter(user=request.user, id=workout_id).prefetch_related('exercises').first()
    if not workout:
        messages.error(request, "Workout not found.")
        return redirect('workouts')

    exercise_cards = []
    for exercise in workout.exercises.all():
        last_log = LiftExerciseLog.objects.filter(
            user=request.user,
            exercise=exercise
        ).order_by('-date', '-id').first()

        exercise_cards.append({
            'exercise': exercise,
            'last_log': last_log,
        })

    return render(request, 'tracker/custom_workout_detail.html', {
        'workout': workout,
        'exercise_cards': exercise_cards,
    })


@login_required
@require_POST
def log_custom_workout(request, workout_id):
    workout = CustomLiftWorkout.objects.filter(user=request.user, id=workout_id).prefetch_related('exercises').first()
    if not workout:
        messages.error(request, "Workout not found.")
        return redirect('workouts')

    for exercise in workout.exercises.all():
        sets_value = _parse_positive_int(request.POST.get(f"sets_{exercise.id}"))
        reps_value = _parse_positive_int(request.POST.get(f"reps_{exercise.id}"))
        weight_value = _parse_nonnegative_float(request.POST.get(f"weight_{exercise.id}"))

        if sets_value and reps_value and weight_value is not None:
            LiftExerciseLog.objects.create(
                user=request.user,
                workout=workout,
                exercise=exercise,
                sets=sets_value,
                reps=reps_value,
                weight=weight_value,
            )

    WorkoutLog.objects.create(
        user=request.user,
        activity_name=workout.name,
        duration=None,
        distance=None,
        color='#9b2915',
    )

    messages.success(request, "Workout saved.")
    return redirect('stats')


@login_required
@require_POST
def log_workout(request):
    activity = request.POST.get('activity')
    distance = _parse_optional_positive_float(request.POST.get('distance'))
    duration = _parse_positive_int(request.POST.get('duration'))

    if not activity:
        messages.error(request, "Pick an activity before logging your workout.")
        return redirect('stats')

    color_map = {
        'Running': '#9b2915',
        'Swimming': '#4d2d18',
        'Cycling': '#e9b44c',
        'HIIT': '#c75c2a',
        'Rowing': '#a67c52',
        'Stair Climber': '#7a3b2e',
        'Elliptical': '#b5653b',
    }

    WorkoutLog.objects.create(
        user=request.user,
        activity_name=activity,
        distance=distance,
        duration=duration,
        color=color_map.get(activity, '#9b2915')
    )
    return redirect('stats')


@login_required
@require_POST
def log_weight(request):
    weight_value = _parse_positive_int(request.POST.get('weight'))
    if weight_value is not None:
        WeightEntry.objects.create(
            user=request.user,
            weight=weight_value
        )

        profile = Profile.objects.filter(user=request.user).first()
        if profile:
            profile.weight = weight_value
            profile.save(update_fields=['weight'])
        messages.success(request, "Weight saved.")
    else:
        messages.error(request, "Enter a valid weight greater than 0.")

    return redirect('stats')


@login_required
def stats(request):
    profile = Profile.objects.filter(user=request.user).first()
    workouts = WorkoutLog.objects.filter(user=request.user).order_by('date')
    weights = list(WeightEntry.objects.filter(user=request.user).order_by('date', 'id'))

    events = []
    for workout in workouts:
        summary_parts = []
        if workout.distance:
            summary_parts.append(f"{workout.distance} mi")
        if workout.duration:
            summary_parts.append(f"{workout.duration} min")

        events.append({
            'title': workout.activity_name,
            'start': (workout.date or timezone.localdate()).isoformat(),
            'color': workout.color,
            'extendedProps': {
                'distance': workout.distance,
                'duration': workout.duration,
                'summary': " • ".join(summary_parts) if summary_parts else "No extra details"
            }
        })

    labels = []
    values = []

    if weights:
        start_date = weights[0].date
        for entry in weights:
            if entry.weight is None or entry.weight <= 0:
                continue

            labels.append((entry.date - start_date).days)
            values.append(float(entry.weight))

    current_weight = values[-1] if values else None
    if current_weight is None and profile and profile.weight:
        current_weight = float(profile.weight)
        labels = [0]
        values = [current_weight]

    context = {
        'profile': profile,
        'current_weight': current_weight,
        'events_json': events,
        'labels_json': labels,
        'values_json': values,
    }
    return render(request, 'tracker/stats.html', context)

@login_required
@require_POST
def log_food(request):
    from .models import FoodLog

    food_name = (request.POST.get('food_name') or "").strip()
    protein = _parse_nonnegative_float(request.POST.get('protein'))
    carbs = _parse_nonnegative_float(request.POST.get('carbs'))
    fats = _parse_nonnegative_float(request.POST.get('fats'))
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if not food_name or protein is None or carbs is None or fats is None:
        error_message = "Enter a food name and valid macro values."
        if is_ajax:
            return JsonResponse({'ok': False, 'message': error_message}, status=400)
        messages.error(request, error_message)
        return redirect('nutrition')

    FoodLog.objects.create(
        user=request.user,
        food_name=food_name,
        protein=protein,
        carbs=carbs,
        fats=fats,
    )
    success_message = f"{food_name} added to your food log."
    if is_ajax:
        return JsonResponse({'ok': True, 'message': success_message})
    messages.success(request, success_message)
    return redirect('nutrition')

@login_required
def update_goals(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        goal, _ = UserGoal.objects.get_or_create(user=request.user)
        
        # 1. Get the specific goal for THIS user
        goal, created = UserGoal.objects.get_or_create(user=request.user)
        
        # 2. Assign the new values from the JS 'body'
        goal.protein_goal = int(data.get('protein'))
        goal.carb_goal = int(data.get('carbs'))
        goal.fat_goal = int(data.get('fats'))
        
        # 3. CRITICAL: This is what makes it stay in the DB
        goal.save() 
        
        return JsonResponse({'status': 'success'})


def get_fatsecret_token():
    url = "https://oauth.fatsecret.com/connect/token"
    data = {
        'grant_type': 'client_credentials',
        'scope': 'basic'
    }
    
    # Debug: Check if settings are actually loading (Don't worry, this only prints to your terminal)
    print(f"DEBUG: Using Client ID: {settings.FATSECRET_CLIENT_ID[:5]}...") 

    response = requests.post(
        url, 
        data=data, 
        auth=(settings.FATSECRET_CLIENT_ID, settings.FATSECRET_CLIENT_SECRET)
    )

    # 1. Check if the token request actually worked
    if response.status_code != 200:
        print(f"!!! TOKEN FAILURE: {response.status_code}")
        print(f"!!! RESPONSE: {response.text}")
        return None

    token = response.json().get('access_token')
    
    # 2. Confirm we got a string back
    if token:
        print("Successfully obtained Access Token.")
    else:
        print("Token request succeeded but 'access_token' was missing from JSON.")
        
    return token

@login_required
def api_food_search(request):
    query = request.GET.get('q', '')
    token = get_fatsecret_token()
    
    # The FatSecret REST endpoint (different from the token URL)
    url = "https://platform.fatsecret.com/rest/server.api"
    
    # FatSecret needs these EXACT keys
    params = {
        'method': 'foods.search',
        'search_expression': query,
        'format': 'json'
    }
    
    headers = {
        'Authorization': f'Bearer {token}'
    }

    # Use 'get' or 'post' - FatSecret supports both, but params must be correct
    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    # --- DEBUG STEP: Paste what this prints into our chat ---
    print("RAW RESPONSE:", data) 
    # -------------------------------------------------------

    # Extract the food list
    # Path: data -> foods -> food
    foods_data = data.get('foods', {})
    results = foods_data.get('food', [])

    # If there's only 1 result, FatSecret sends a dict. Convert to list.
    if isinstance(results, dict):
        results = [results]

    return JsonResponse({'results': results})