from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm


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
def stats(request):
    profile = request.user.profile
    weight = profile.weight
    goal = profile.goal_weight

    # Scale the bar so the larger of the two values sits at 90% width,
    # leaving room for the smaller segment to be visible
    bar_max = max(weight, goal) / 0.9

    lower_pct = round((min(weight, goal) / bar_max) * 100, 2)
    upper_pct = round((max(weight, goal) / bar_max) * 100, 2)
    delta_pct = round(upper_pct - lower_pct, 2)

    gaining = goal > weight

    context = {
        'lower_pct': lower_pct,
        'upper_pct': upper_pct,
        'delta_pct': delta_pct,
        'gaining': gaining,
        'weight': weight,
        'goal': goal,
    }
    return render(request, "tracker/stats.html", context)


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
        "Planet Fitness",
        "Crunch Fitness",
        "Life Time Fitness"
    ]

    context = {
        'workout_name': workout_name,
        'gym_options': gym_options
    }
    return render(request, 'tracker/workout_setup.html', context)