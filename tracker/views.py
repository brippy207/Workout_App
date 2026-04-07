from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone

from .forms import SignUpForm
from .models import WorkoutLog, WeightEntry, Profile

import json
import requests
from django.conf import settings
from django.http import JsonResponse
from django.core.cache import cache


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
@login_required
def proxy_food_search(request):
    query = request.GET.get('query', '').lower().strip()
    
    # 1. THE "PRESENTATION SAVER" (Local Mock Data)
    # If the user types these exact words, it won't even try the API
    mock_db = {
        "apple": {
            "products": [{
                "product_name": "red apple (fresh)",
                "brands": "generic",
                "image_front_small_url": "https://upload.wikimedia.org/wikipedia/commons/1/15/Red_Apple.jpg",
                "nutriments": {"proteins_100g": 0.3, "carbohydrates_100g": 14, "fat_100g": 0.2}
            }]
        },
        "chicken": {
            "products": [{
                "product_name": "chicken breast (grilled)",
                "brands": "poultry",
                "image_front_small_url": "https://upload.wikimedia.org/wikipedia/commons/3/3d/Grilled_Chicken_Breast.jpg",
                "nutriments": {"proteins_100g": 31, "carbohydrates_100g": 0, "fat_100g": 3.6}
            }]
        },
        "cheetos": {
            "products": [{
                "product_name": "cheetos crunchy",
                "brands": "frito lay",
                "image_front_small_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Cheetos-Crunchy.jpg",
                "nutriments": {"proteins_100g": 5.8, "carbohydrates_100g": 53.0, "fat_100g": 35.0}
            }]
        },
        "oreo": {
            "products": [{
                "product_name": "oreo double stuf",
                "brands": "nabisco",
                "image_front_small_url": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Oreo-Two-Cookies.jpg",
                "nutriments": {"proteins_100g": 3, "carbohydrates_100g": 68, "fat_100g": 21}
            }]
        },
        "pizza": {
            "products": [{
                "product_name": "pepperoni pizza",
                "brands": "frozen/delivery",
                "image_front_small_url": "https://upload.wikimedia.org/wikipedia/commons/a/a3/Eq_it-na_pizza-margherita_sep2005_sml.jpg",
                "nutriments": {"proteins_100g": 12, "carbohydrates_100g": 26, "fat_100g": 10}
            }]
        }
    }

    if query in mock_db:
        return JsonResponse(mock_db[query])

    # 2. THE REAL API CALL (If not in mock_db)
    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&search_simple=1&action=process&json=1&page_size=20&fields=product_name,nutriments,image_front_small_url,brands"
    headers = {'User-Agent': 'MyRetroApp/1.0'}

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        return JsonResponse(response.json())
    except:
        # 3. THE FAIL-SAFE: If the API is 503/Down, return an empty list instead of a crash
        return JsonResponse({"products": []})

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
    return render(request, 'tracker/workout_setup.html', {
        'workout_name': workout_name,
        'gym_options': gym_options
    })


@login_required
@require_POST
def log_workout(request):
    activity = request.POST.get('activity')
    distance = request.POST.get('distance') or None
    duration = request.POST.get('duration') or None

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
    weight_value = request.POST.get('weight')
    if weight_value:
        WeightEntry.objects.create(
            user=request.user,
            weight=weight_value
        )

        profile = Profile.objects.filter(user=request.user).first()
        if profile:
            profile.weight = weight_value
            profile.save(update_fields=['weight'])

    return redirect('stats')


@login_required
def stats(request):
    profile = Profile.objects.filter(user=request.user).first()
    workouts = WorkoutLog.objects.filter(user=request.user).order_by('date')
    weights = WeightEntry.objects.filter(user=request.user).order_by('date')

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

    values = [
    float(entry.weight)
    for entry in weights
    if entry.weight is not None and float(entry.weight) > 0
]

    if profile and profile.weight:
        start_weight = float(profile.weight)
    elif values:
        start_weight = float(values[0])
    else:
        start_weight = 0

    # x-axis = day count starting at 0
    labels = []

    if weights:
        start_date = weights[0].date
        for entry in weights:
            days_since_start = (entry.date - start_date).days
            labels.append(days_since_start)

        labels = [0] + labels
    else:
        labels = [0]
    values = [start_weight] + values

    current_weight = values[-1] if values else start_weight

    context = {
        'profile': profile,
        'current_weight': current_weight,
        'events_json': events,
        'labels_json': labels,
        'values_json': values,
    }
    return render(request, 'tracker/stats.html', context)

@login_required
def nutrition(request):
    from .models import FoodLog
    today = timezone.localdate()
    food_logs = FoodLog.objects.filter(user=request.user, date=today)
    return render(request, 'tracker/nutrition.html', {'food_logs': food_logs})

@login_required
@require_POST
def log_food(request):
    from .models import FoodLog
    FoodLog.objects.create(
        user=request.user,
        food_name=request.POST.get('food_name'),
        protein=float(request.POST.get('protein', 0)),
        carbs=float(request.POST.get('carbs', 0)),
        fats=float(request.POST.get('fats', 0)),
    )
    return redirect('nutrition')


@require_POST
def search_food(request):
    """Proxy endpoint that forwards search queries to the USDA FDC API.
    Keeps the API key on the server and caches results for 30 minutes.
    """
    try:
        payload = json.loads(request.body.decode() or "{}")
        query = (payload.get('query') or "").strip()
        if not query:
            return JsonResponse({'foods': []})

        cache_key = f"usda_search:{query.lower()}"
        cached = cache.get(cache_key)
        if cached:
            return JsonResponse({'foods': cached})

        url = 'https://api.nal.usda.gov/fdc/v1/foods/search'
        params = {'api_key': getattr(settings, 'USDA_API_KEY', ''), 'query': query}
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()

        foods = []
        for f in data.get('foods', [])[:25]:
            foods.append({
                'description': f.get('description'),
                'foodNutrients': [
                    {'nutrientName': n.get('nutrientName'), 'value': n.get('value')}
                    for n in f.get('foodNutrients', [])
                ],
                'servingsPerContainer': f.get('servingsPerContainer')
            })

        cache.set(cache_key, foods, 60 * 30)  # cache 30 minutes
        return JsonResponse({'foods': foods})
    except Exception:
        return JsonResponse({'foods': []}, status=500)