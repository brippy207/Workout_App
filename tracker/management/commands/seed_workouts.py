from django.core.management.base import BaseCommand
from tracker.models import WorkoutTemplate, WorkoutExercise

WORKOUTS = {
    ("legs", "home_gym"): {
        "name": "At-Home Leg Workout",
        "description": "A lower-body workout built for dumbbells, a bench/box, and common home-gym equipment.",
        "exercises": [
            ("Goblet Squat", 1, 4, "8-12", 90, "Keep torso tall and control the lowering phase."),
            ("Romanian Deadlift", 2, 4, "8-12", 90, "Hinge at the hips and keep dumbbells close."),
            ("Bulgarian Split Squat", 3, 3, "8-10 / side", 90, "Rear foot elevated if available."),
            ("Dumbbell Hip Thrust", 4, 3, "10-15", 75, "Pause at the top."),
            ("Standing Calf Raise", 5, 3, "12-20", 60, "Full stretch and full lockout."),
        ],
    },
    ("legs", "planet_fitness"): {
        "name": "Planet Fitness Leg Workout",
        "description": "A lower-body workout designed around common Planet Fitness equipment.",
        "exercises": [
            ("Smith Machine Squat", 1, 4, "6-10", 120, "Brace hard and keep stance consistent."),
            ("Leg Press", 2, 4, "10-15", 90, "Use a controlled depth you can own."),
            ("Romanian Deadlift (Smith or Dumbbells)", 3, 3, "8-12", 90, "Hinge, do not squat the movement."),
            ("Leg Curl Machine", 4, 3, "10-15", 75, "Control both directions."),
            ("Leg Extension", 5, 3, "12-15", 60, "Smooth tempo, no bouncing."),
            ("Calf Raise on Leg Press or Smith", 6, 3, "12-20", 60, "Pause at the stretched bottom."),
        ],
    },
    ("legs", "commercial"): {
        "name": "Commercial Gym Leg Workout",
        "description": "A balanced hypertrophy-focused leg workout for a standard gym.",
        "exercises": [
            ("Barbell Back Squat", 1, 4, "5-8", 120, "Use full-body tension and consistent depth."),
            ("Romanian Deadlift", 2, 4, "6-10", 120, "Push hips back, slight knee bend."),
            ("Leg Press", 3, 3, "10-15", 90, "Drive through the mid-foot."),
            ("Walking Lunges", 4, 3, "10-12 / side", 90, "Long enough stride to load glutes and quads."),
            ("Leg Curl", 5, 3, "10-15", 75, "Control the eccentric."),
            ("Standing Calf Raise", 6, 4, "12-20", 60, "Pause top and bottom."),
        ],
    },
    ("legs", "crunch"): {
        "name": "Crunch Fitness Leg Workout",
        "description": "A leg workout for a gym with free weights plus a standard machine lineup.",
        "exercises": [
            ("Barbell or Dumbbell Squat", 1, 4, "6-10", 120, "Choose the heaviest stable setup available."),
            ("Romanian Deadlift", 2, 4, "8-10", 90, "Keep lats engaged."),
            ("Leg Press or Hack Squat", 3, 3, "10-15", 90, "Use the machine your club has free."),
            ("Bulgarian Split Squat", 4, 3, "8-10 / side", 90, "Controlled descent."),
            ("Leg Curl", 5, 3, "10-15", 75, "Do not swing."),
            ("Calf Raise", 6, 3, "12-20", 60, "Use full ROM."),
        ],
    },
    ("legs", "life_time"): {
        "name": "Life Time Leg Workout",
        "description": "A fuller lower-body workout built for a well-equipped gym floor.",
        "exercises": [
            ("Barbell Back Squat", 1, 4, "5-8", 120, "Main strength movement."),
            ("Romanian Deadlift", 2, 4, "6-10", 120, "Posterior-chain emphasis."),
            ("Hack Squat or Pendulum Squat", 3, 3, "8-12", 90, "Controlled bottom position."),
            ("Walking Dumbbell Lunges", 4, 3, "10-12 / side", 90, "Stay upright."),
            ("Seated Leg Curl", 5, 3, "10-15", 75, "Squeeze hamstrings hard."),
            ("Leg Extension", 6, 2, "12-15", 60, "Finish with controlled isolation."),
            ("Standing Calf Raise", 7, 4, "12-20", 60, "Pause at the top."),
        ],
    },
}
# Add the same structure for chest, back, arms, push, pull, upper, full_body.
# Start with legs + upper + push/pull first, then expand.

class Command(BaseCommand):
    help = "Seed default workout templates"

    def handle(self, *args, **kwargs):
        for (category, gym_type), payload in WORKOUTS.items():
            workout, _ = WorkoutTemplate.objects.get_or_create(
                category=category,
                gym_type=gym_type,
                defaults={
                    "name": payload["name"],
                    "description": payload["description"],
                },
            )

            if workout.exercises.exists():
                continue

            for name, order, sets, reps, rest, notes in payload["exercises"]:
                WorkoutExercise.objects.create(
                    workout=workout,
                    order=order,
                    name=name,
                    sets=sets,
                    reps=reps,
                    rest_seconds=rest,
                    notes=notes,
                )

        self.stdout.write(self.style.SUCCESS("Workout templates seeded."))