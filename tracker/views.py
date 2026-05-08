from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db import DatabaseError
from django.http import JsonResponse
from django.db.models import Sum
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import FoodLog, UserGoal 
import google.generativeai as genai
import ast

from .forms import SignUpForm
from .models import (
    WorkoutLog,
    WeightEntry,
    Profile,
    CustomLiftWorkout,
    CustomLiftExercise,
    LiftExerciseLog,
    WorkoutTemplate,
    WorkoutExercise,
    UserExercisePerformance,
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
def nutrition(request):
    goal, _ = UserGoal.objects.get_or_create(user=request.user)

    # 2. Get today's logs
    today = timezone.now().date()
    daily_logs = FoodLog.objects.filter(user=request.user, date=today)

    # 3. DEFINE 'totals' HERE (Must be before you use it!)
    totals = daily_logs.aggregate(
        total_p=Sum('protein'),
        total_c=Sum('carbs'),
        total_f=Sum('fats')
    )

    # 4. Extract values safely (handling None cases)
    p = totals.get('total_p') or 0
    c = totals.get('total_c') or 0
    f = totals.get('total_f') or 0

    # 5. Now do your math
    consumed_cals = (p * 4) + (c * 4) + (f * 9)
    goal_cals = (goal.protein_goal * 4) + (goal.carb_goal * 4) + (goal.fat_goal * 9)

    # 6. Pass everything to the template
    context = {
        'goal': goal,
        'consumed_p': int(p),
        'consumed_c': int(c),
        'consumed_f': int(f),
        'consumed_cals': int(consumed_cals), # int() makes it look cleaner in HTML
        'goal_cals': int(goal_cals),
        'food_logs': daily_logs,  # keep this for the template loop
        'food_logs_json': list(daily_logs.values('food_name', 'protein', 'carbs', 'fats')),
    }

    return render(request, 'tracker/nutrition.html', context)


@login_required
def workouts(request):
    custom_workouts = CustomLiftWorkout.objects.filter(user=request.user).order_by('-id')
    return render(request, 'tracker/workouts.html', {
        'custom_workouts': custom_workouts
    })


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
        'lifting_cards': [],
    }

    if name == 'lifting':
        context['custom_workouts'] = CustomLiftWorkout.objects.filter(
            user=request.user
        ).order_by('-id')

        context['lifting_cards'] = [
            {
                'name': item,
                'slug': item,
            }
            for item in data['lifting']
        ]

    return render(request, 'tracker/category_detail.html', context)

@login_required
def saved_workouts(request):
    custom_workouts = CustomLiftWorkout.objects.filter(
        user=request.user
    ).order_by('-id')

    return render(request, 'tracker/saved_workouts.html', {
        'custom_workouts': custom_workouts
    })


@login_required
def workout_setup(request, workout_name):
    gym_options = [
        ("bodyweight", "No Equipment (Bodyweight)"),
        ("home_gym", "Home Gym / Dumbbells"),
        ("commercial", "General Commercial Gym"),
        ("planet_fitness", "Planet Fitness"),
        ("crunch", "Crunch Fitness"),
        ("life_time", "Life Time Fitness"),
    ]

    return render(request, "tracker/workout_setup.html", {
        "workout_name": workout_name,
        "gym_options": gym_options,
    })


@login_required
def get_premade_workout(request, workout_name, gym_type):
    normalized = workout_name.lower().replace(" ", "_")

    workout = get_object_or_404(
        WorkoutTemplate,
        category=normalized,
        gym_type=gym_type
    )

    exercises = []

    for exercise in workout.exercises.all():
        latest = UserExercisePerformance.objects.filter(
            user=request.user,
            workout=workout,
            exercise=exercise
        ).first()

        exercises.append({
            "id": exercise.id,
            "name": exercise.name,
            "order": exercise.order,
            "sets": exercise.sets,
            "reps": exercise.reps,
            "rest_seconds": exercise.rest_seconds,
            "notes": exercise.notes,
            "previous": {
                "set_1_weight": latest.set_1_weight if latest else None,
                "set_1_reps": latest.set_1_reps if latest else None,
                "set_2_weight": latest.set_2_weight if latest else None,
                "set_2_reps": latest.set_2_reps if latest else None,
                "set_3_weight": latest.set_3_weight if latest else None,
                "set_3_reps": latest.set_3_reps if latest else None,
                "set_4_weight": latest.set_4_weight if latest else None,
                "set_4_reps": latest.set_4_reps if latest else None,
                "notes": latest.notes if latest else "",
            }
        })

    return JsonResponse({
        "workout": {
            "name": workout.name,
            "description": workout.description,
            "slug": workout.slug,
        },
        "exercises": exercises
    })


@login_required
@require_POST
def save_premade_workout_progress(request, workout_slug):
    workout = get_object_or_404(WorkoutTemplate, slug=workout_slug)

    saved_anything = False

    for exercise in workout.exercises.all():
        prefix = f"exercise_{exercise.id}_"

        def f(name):
            value = request.POST.get(prefix + name)
            return float(value) if value not in (None, "") else None

        def i(name):
            value = request.POST.get(prefix + name)
            return int(value) if value not in (None, "") else None

        has_any_value = any(
            request.POST.get(prefix + field)
            for field in [
                "set_1_weight", "set_1_reps",
                "set_2_weight", "set_2_reps",
                "set_3_weight", "set_3_reps",
                "set_4_weight", "set_4_reps",
            ]
        )

        if not has_any_value:
            continue

        UserExercisePerformance.objects.create(
            user=request.user,
            workout=workout,
            exercise=exercise,
            set_1_weight=f("set_1_weight"),
            set_1_reps=i("set_1_reps"),
            set_2_weight=f("set_2_weight"),
            set_2_reps=i("set_2_reps"),
            set_3_weight=f("set_3_weight"),
            set_3_reps=i("set_3_reps"),
            set_4_weight=f("set_4_weight"),
            set_4_reps=i("set_4_reps"),
            notes=request.POST.get(prefix + "notes", "").strip(),
        )

        saved_anything = True

    if saved_anything:
        WorkoutLog.objects.create(
            user=request.user,
            activity_name=workout.name,
            duration=None,
            distance=None,
            color='#d46a1f',
        )
        messages.success(request, "Premade workout progress saved.")
    else:
        messages.error(request, "Enter at least one set before saving.")

    return redirect('workout_setup', workout_name=workout.category.replace("_", " ").title())


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

        saved_exercises = 0

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
                saved_exercises += 1

        if saved_exercises == 0:
            workout.delete()
            messages.error(request, "Add at least one valid exercise.")
            return redirect('create_custom_workout')

        messages.success(request, "Custom workout saved.")
        return redirect('custom_workout_detail', workout_id=workout.id)

    return render(request, 'tracker/custom_workout_builder.html')

def analyze_food_image(request):
    """
    Analyzes an uploaded food image using Gemini 2.5 and returns 
    macro estimates in a format compatible with the Manual Entry panel.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

    try:
        # 1. Grab the image
        image_file = request.FILES.get('image')
        if not image_file:
            return JsonResponse({'error': 'No image uploaded'}, status=400)

        # 2. Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Using the 2.5 version you confirmed exists in your model list
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        user_extra_context = request.POST.get('user_context', '')

        # 3. Define a strict prompt to minimize formatting errors
        base_prompt = (
            "Identify the food in this image. Give an estimate of how many grams of protein, carbs, and fat are on the WHOLE PLATE/BOWL."
            "If you cannot identify any food in the image, return exactly: 'No food found'. Do not try to identify food that looks like it's not there."
            "Otherwise, return ONLY a JSON object with double quotes. "
            "Fields: 'food_name' (string), 'protein' (int), 'carbs' (int), 'fats' (int), 'calories' (int). "
            "Do not include any conversational text or markdown."
        )
        
        # If the user provided context, append it to the prompt
        if user_extra_context:
            full_prompt = f"{base_prompt}\n\nUSER PROVIDED CONTEXT: {user_extra_context}"
        else:
            full_prompt = base_prompt

        # 4. Get response
        response = model.generate_content([
            full_prompt,
            {'mime_type': image_file.content_type, 'data': image_file.read()}
        ])

        if not response.text:
            return JsonResponse({'error': 'AI returned an empty response'}, status=500)
        
        if "No food found" in response.text:
            return JsonResponse({'error': 'No food recognized. Please try a clearer photo!'}, status=400)

        # 5. Clean the response text (Strip Markdown backticks if present)
        raw_text = response.text.strip()
        if "```" in raw_text:
            # Extract content between backticks
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        
        raw_text = raw_text.strip()

        # 6. Parse the data (The "Double Guard" method)
        try:
            # Try standard JSON first (expects double quotes)
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            # Fallback to literal_eval (handles single quotes/Python dict format)
            data = ast.literal_eval(raw_text)

        # 7. Return to frontend (mapping keys to match your JS IDs)
        return JsonResponse({
            'food_name': data.get('food_name', 'Unknown Food'),
            'protein': data.get('protein', 0),
            'carbs': data.get('carbs', 0),
            'fats': data.get('fats', 0),
            'calories': data.get('calories', 0),
            'serving_amount': 1
        })

    except Exception as e:
        # Log the specific error to the terminal for debugging
        print(f"--- ANALYZE ERROR --- \n{str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def custom_workout_detail(request, workout_id):
    workout = CustomLiftWorkout.objects.filter(
        user=request.user,
        id=workout_id
    ).prefetch_related('exercises').first()

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
    workout = CustomLiftWorkout.objects.filter(
        user=request.user,
        id=workout_id
    ).prefetch_related('exercises').first()

    if not workout:
        messages.error(request, "Workout not found.")
        return redirect('workouts')

    saved_anything = False

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
            saved_anything = True

    if saved_anything:
        WorkoutLog.objects.create(
            user=request.user,
            activity_name=workout.name,
            duration=None,
            distance=None,
            color='#9b2915',
        )
        messages.success(request, "Workout saved.")
        return redirect('stats')

    messages.error(request, "Enter at least one valid exercise log.")
    return redirect('custom_workout_detail', workout_id=workout.id)


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
    workout_logs = WorkoutLog.objects.filter(user=request.user).order_by('date')
    weights = list(WeightEntry.objects.filter(user=request.user).order_by('date', 'id'))

    events = []
    for workout in workout_logs:
        summary_parts = []
        if workout.distance:
            summary_parts.append(str(workout.distance) + ' mi')
        if workout.duration:
            summary_parts.append(str(workout.duration) + ' min')
        events.append({
            'title': workout.activity_name,
            'start': (workout.date or timezone.localdate()).isoformat(),
            'color': workout.color,
            'extendedProps': {
                'distance': workout.distance,
                'duration': workout.duration,
                'summary': ' • '.join(summary_parts) if summary_parts else 'No extra details'
            }
        })

    # Build workout details by date
    workout_details_by_date = {}
    for workout in workout_logs:
        key = (workout.date or timezone.localdate()).isoformat()
        if key not in workout_details_by_date:
            workout_details_by_date[key] = []

        # Query UserExercisePerformance instead
        perf_logs = UserExercisePerformance.objects.filter(
            user=request.user,
            performed_on=workout.date
        ).select_related('exercise', 'workout')

        exercises = []
        for log in perf_logs:
            sets_data = []
            if log.set_1_weight is not None and log.set_1_reps is not None:
                sets_data.append(str(log.set_1_reps) + ' reps @ ' + str(log.set_1_weight) + ' lbs')
            if log.set_2_weight is not None and log.set_2_reps is not None:
                sets_data.append(str(log.set_2_reps) + ' reps @ ' + str(log.set_2_weight) + ' lbs')
            if log.set_3_weight is not None and log.set_3_reps is not None:
                sets_data.append(str(log.set_3_reps) + ' reps @ ' + str(log.set_3_weight) + ' lbs')
            if log.set_4_weight is not None and log.set_4_reps is not None:
                sets_data.append(str(log.set_4_reps) + ' reps @ ' + str(log.set_4_weight) + ' lbs')
            exercises.append({
                'name': log.exercise.name,
                'sets': sets_data,
                'notes': log.notes or '',
            })

        workout_details_by_date[key].append({
            'name': workout.activity_name,
            'distance': workout.distance,
            'duration': workout.duration,
            'exercises': exercises,
        })

    nutrition_events = []
    daily_nutrition = FoodLog.objects.filter(user=request.user).values('date').annotate(
        total_p=Sum('protein'),
        total_c=Sum('carbs'),
        total_f=Sum('fats')
    ).order_by('date')
    for day in daily_nutrition:
        cals = int((day['total_p'] * 4) + (day['total_c'] * 4) + (day['total_f'] * 9))
        nutrition_events.append({
            'date': day['date'].isoformat(),
            'cals': cals,
            'protein': int(day['total_p']),
            'carbs': int(day['total_c']),
            'fats': int(day['total_f']),
        })

    food_logs_by_date = {}
    for log in FoodLog.objects.filter(user=request.user):
        key = log.date.isoformat()
        if key not in food_logs_by_date:
            food_logs_by_date[key] = []
        food_logs_by_date[key].append({
            'name': log.food_name,
            'protein': log.protein,
            'carbs': log.carbs,
            'fats': log.fats,
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
        'nutrition_events_json': nutrition_events,
        'food_logs_by_date_json': food_logs_by_date,
        'workout_details_by_date_json': workout_details_by_date,
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

    # 1. Create the new entry
    # Note: Ensure your model uses 'date' as the field name as per your previous error
    FoodLog.objects.create(
        user=request.user,
        food_name=food_name,
        protein=protein,
        carbs=carbs,
        fats=fats,
        date=timezone.now().date() 
    )

    # 2. Calculate the NEW totals for today
    today = timezone.now().date()
    totals = FoodLog.objects.filter(user=request.user, date=today).aggregate(
        total_p=Sum('protein'),
        total_c=Sum('carbs'),
        total_f=Sum('fats')
    )

    # 3. Clean the data (convert None to 0)
    p = totals.get('total_p') or 0
    c = totals.get('total_c') or 0
    f = totals.get('total_f') or 0
    
    # 4. Calculate total calories based on the NEW totals
    new_calories = (p * 4) + (c * 4) + (f * 9)

    success_message = f"{food_name} added to your food log."
    
    if is_ajax:
        # Return the new totals so JS doesn't have to guess
        return JsonResponse({
            'ok': True, 
            'message': success_message,
            'new_total_p': p,
            'new_total_c': c,
            'new_total_f': f,
            'new_calories': int(new_calories)
        })

    messages.success(request, success_message)
    return redirect('nutrition')

@login_required
def update_goals(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        goal, _ = UserGoal.objects.get_or_create(user=request.user)
        
        # 1. Get the specific goal for THIS user
        goal, _ = UserGoal.objects.get_or_create(user=request.user)
        
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