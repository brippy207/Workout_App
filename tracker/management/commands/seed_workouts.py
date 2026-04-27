from django.core.management.base import BaseCommand
from tracker.models import WorkoutTemplate, WorkoutExercise


GYM_LABELS = {
    "bodyweight": "No Equipment",
    "home_gym": "Home Gym",
    "commercial": "Commercial Gym",
    "planet_fitness": "Planet Fitness",
    "crunch": "Crunch Fitness",
    "life_time": "Life Time Fitness",
}


BASE_WORKOUTS = {
    "chest": {
        "description": "A balanced chest-focused session with pressing plus isolation work.",
        "exercises": [
            ("Primary Press", 4, "6-10", 120, "Main heavy chest press."),
            ("Secondary Press", 3, "8-12", 90, "Slight angle change from primary press."),
            ("Chest Fly", 3, "10-15", 75, "Controlled stretch and squeeze."),
            ("Dip / Push-Up Pattern", 3, "8-15", 75, "Stop 1-2 reps shy of failure."),
            ("Triceps Finisher", 2, "12-15", 60, "Keep elbows tucked."),
        ],
    },
    "back": {
        "description": "A back-focused workout built around vertical and horizontal pulling.",
        "exercises": [
            ("Vertical Pull", 4, "6-10", 120, "Use full range and control."),
            ("Horizontal Row", 4, "8-12", 90, "Pull elbow toward hip."),
            ("Secondary Row", 3, "10-12", 75, "Focus on mid-back contraction."),
            ("Rear Delt / Upper Back", 3, "12-20", 60, "Lighter weight, strict form."),
            ("Biceps Finisher", 2, "10-15", 60, "Controlled reps."),
        ],
    },
    "arms": {
        "description": "A direct arms session emphasizing biceps, triceps, and forearm stability.",
        "exercises": [
            ("Heavy Curl", 3, "8-10", 75, "No swinging."),
            ("Stretch Curl", 3, "10-12", 60, "Use full elbow extension."),
            ("Heavy Triceps Press", 3, "8-10", 75, "Lock out under control."),
            ("Overhead Triceps", 3, "10-12", 60, "Good long-head emphasis."),
            ("Lateral Raise", 3, "12-20", 45, "Strict tempo."),
            ("Forearm / Grip", 2, "12-20", 45, "Optional finisher."),
        ],
    },
    "legs": {
        "description": "A lower-body workout covering quads, glutes, hamstrings, and calves.",
        "exercises": [
            ("Primary Squat Pattern", 4, "6-10", 120, "Main leg movement."),
            ("Hip Hinge", 4, "8-10", 120, "Keep spine neutral."),
            ("Single-Leg Movement", 3, "8-12 / side", 90, "Control each rep."),
            ("Leg Curl Pattern", 3, "10-15", 75, "Focus on hamstrings."),
            ("Calf Raise", 4, "12-20", 60, "Pause top and bottom."),
        ],
    },
    "push": {
        "description": "A push day emphasizing chest, shoulders, and triceps.",
        "exercises": [
            ("Flat / Main Press", 4, "6-10", 120, "Primary upper-body push."),
            ("Overhead Press", 3, "6-10", 90, "Brace the core."),
            ("Incline Press", 3, "8-12", 90, "Upper chest emphasis."),
            ("Lateral Raise", 3, "12-20", 45, "Strict reps."),
            ("Triceps Pressdown / Extension", 3, "10-15", 60, "Full elbow extension."),
        ],
    },
    "pull": {
        "description": "A pull day for lats, upper back, rear delts, and biceps.",
        "exercises": [
            ("Vertical Pull", 4, "6-10", 120, "Drive elbows down."),
            ("Main Row", 4, "8-12", 90, "Keep torso stable."),
            ("Secondary Pull", 3, "10-12", 75, "Squeeze upper back."),
            ("Rear Delt Fly / Face Pull", 3, "12-20", 60, "Light and controlled."),
            ("Curl Variation", 3, "10-15", 60, "No momentum."),
        ],
    },
    "upper": {
        "description": "A balanced upper-body day with push and pull volume in one session.",
        "exercises": [
            ("Horizontal Press", 4, "6-10", 120, "Main press."),
            ("Horizontal Row", 4, "8-12", 90, "Main row."),
            ("Vertical Press", 3, "8-12", 75, "Shoulder focus."),
            ("Vertical Pull", 3, "8-12", 75, "Lat focus."),
            ("Biceps", 2, "10-15", 60, "Arm assistance."),
            ("Triceps", 2, "10-15", 60, "Arm assistance."),
        ],
    },
    "full_body": {
        "description": "A science-based full-body workout built around efficient compound lifts.",
        "exercises": [
            ("Squat Pattern", 3, "5-8", 120, "Main lower-body compound."),
            ("Press Pattern", 3, "6-10", 90, "Main upper-body push."),
            ("Row / Pull Pattern", 3, "8-12", 90, "Main upper-body pull."),
            ("Hip Hinge", 3, "8-10", 90, "Posterior chain."),
            ("Single-Joint Upper", 2, "10-15", 60, "Arms or delts."),
            ("Core / Conditioning Finisher", 2, "30-60 sec", 45, "Optional finish."),
        ],
    },
}


EXERCISE_SUBSTITUTIONS = {
    "bodyweight": {
        "Primary Press": "Push-Up",
        "Secondary Press": "Deficit Push-Up",
        "Chest Fly": "Floor Chest Fly with Bands",
        "Dip / Push-Up Pattern": "Bench Dip",
        "Triceps Finisher": "Diamond Push-Up",

        "Vertical Pull": "Band Lat Pulldown",
        "Horizontal Row": "Inverted Row",
        "Secondary Row": "Band Row",
        "Rear Delt / Upper Back": "Band Face Pull",
        "Biceps Finisher": "Band Curl",

        "Heavy Curl": "Band Curl",
        "Stretch Curl": "Incline Band Curl",
        "Heavy Triceps Press": "Close-Grip Push-Up",
        "Overhead Triceps": "Band Overhead Triceps Extension",
        "Lateral Raise": "Band Lateral Raise",
        "Forearm / Grip": "Towel Hang",

        "Primary Squat Pattern": "Bodyweight Squat",
        "Hip Hinge": "Single-Leg Romanian Deadlift",
        "Single-Leg Movement": "Reverse Lunge",
        "Leg Curl Pattern": "Sliding Leg Curl",
        "Calf Raise": "Single-Leg Calf Raise",

        "Flat / Main Press": "Push-Up",
        "Overhead Press": "Pike Push-Up",
        "Incline Press": "Feet-Elevated Push-Up",
        "Triceps Pressdown / Extension": "Band Triceps Pressdown",

        "Main Row": "Inverted Row",
        "Secondary Pull": "Band Straight-Arm Pulldown",
        "Rear Delt Fly / Face Pull": "Band Face Pull",
        "Curl Variation": "Band Curl",

        "Horizontal Press": "Push-Up",
        "Vertical Press": "Pike Push-Up",
        "Vertical Pull": "Band Lat Pulldown",
        "Biceps": "Band Curl",
        "Triceps": "Diamond Push-Up",

        "Squat Pattern": "Bodyweight Squat",
        "Press Pattern": "Push-Up",
        "Row / Pull Pattern": "Inverted Row",
        "Single-Joint Upper": "Band Curl + Band Triceps Extension",
        "Core / Conditioning Finisher": "Plank",
    },

    "home_gym": {
        "Primary Press": "Dumbbell Bench Press",
        "Secondary Press": "Incline Dumbbell Press",
        "Chest Fly": "Dumbbell Fly",
        "Dip / Push-Up Pattern": "Weighted Push-Up",
        "Triceps Finisher": "Overhead Dumbbell Triceps Extension",

        "Vertical Pull": "Band Lat Pulldown or Pull-Up",
        "Horizontal Row": "One-Arm Dumbbell Row",
        "Secondary Row": "Chest-Supported Dumbbell Row",
        "Rear Delt / Upper Back": "Rear Delt Fly",
        "Biceps Finisher": "Alternating Dumbbell Curl",

        "Heavy Curl": "Alternating Dumbbell Curl",
        "Stretch Curl": "Incline Dumbbell Curl",
        "Heavy Triceps Press": "Close-Grip Dumbbell Press",
        "Overhead Triceps": "Overhead Dumbbell Triceps Extension",
        "Lateral Raise": "Dumbbell Lateral Raise",
        "Forearm / Grip": "Hammer Curl",

        "Primary Squat Pattern": "Goblet Squat",
        "Hip Hinge": "Dumbbell Romanian Deadlift",
        "Single-Leg Movement": "Bulgarian Split Squat",
        "Leg Curl Pattern": "Stability Ball Leg Curl",
        "Calf Raise": "Standing Dumbbell Calf Raise",

        "Flat / Main Press": "Dumbbell Bench Press",
        "Overhead Press": "Seated Dumbbell Shoulder Press",
        "Incline Press": "Incline Dumbbell Press",
        "Triceps Pressdown / Extension": "Overhead Dumbbell Triceps Extension",

        "Main Row": "One-Arm Dumbbell Row",
        "Secondary Pull": "Chest-Supported Dumbbell Row",
        "Rear Delt Fly / Face Pull": "Rear Delt Fly",
        "Curl Variation": "Hammer Curl",

        "Horizontal Press": "Dumbbell Bench Press",
        "Vertical Press": "Seated Dumbbell Shoulder Press",
        "Vertical Pull": "Band Lat Pulldown or Pull-Up",
        "Biceps": "Incline Dumbbell Curl",
        "Triceps": "Skull Crusher",

        "Squat Pattern": "Goblet Squat",
        "Press Pattern": "Dumbbell Bench Press",
        "Row / Pull Pattern": "One-Arm Dumbbell Row",
        "Single-Joint Upper": "Lateral Raise",
        "Core / Conditioning Finisher": "Farmer Carry",
    },

    "commercial": {
        "Primary Press": "Barbell Bench Press",
        "Secondary Press": "Incline Dumbbell Press",
        "Chest Fly": "Cable Fly",
        "Dip / Push-Up Pattern": "Weighted Dip",
        "Triceps Finisher": "Cable Pressdown",

        "Vertical Pull": "Lat Pulldown",
        "Horizontal Row": "Chest-Supported Row",
        "Secondary Row": "Seated Cable Row",
        "Rear Delt / Upper Back": "Face Pull",
        "Biceps Finisher": "EZ-Bar Curl",

        "Heavy Curl": "EZ-Bar Curl",
        "Stretch Curl": "Incline Dumbbell Curl",
        "Heavy Triceps Press": "Close-Grip Bench Press",
        "Overhead Triceps": "Cable Overhead Triceps Extension",
        "Lateral Raise": "Cable Lateral Raise",
        "Forearm / Grip": "Hammer Curl",

        "Primary Squat Pattern": "Barbell Back Squat",
        "Hip Hinge": "Romanian Deadlift",
        "Single-Leg Movement": "Walking Lunge",
        "Leg Curl Pattern": "Seated Leg Curl",
        "Calf Raise": "Standing Calf Raise",

        "Flat / Main Press": "Barbell Bench Press",
        "Overhead Press": "Seated Dumbbell Shoulder Press",
        "Incline Press": "Incline Barbell Press",
        "Triceps Pressdown / Extension": "Cable Pressdown",

        "Main Row": "Barbell Row",
        "Secondary Pull": "Seated Cable Row",
        "Rear Delt Fly / Face Pull": "Face Pull",
        "Curl Variation": "EZ-Bar Curl",

        "Horizontal Press": "Barbell Bench Press",
        "Vertical Press": "Machine Shoulder Press",
        "Vertical Pull": "Lat Pulldown",
        "Biceps": "Cable Curl",
        "Triceps": "Cable Pressdown",

        "Squat Pattern": "Barbell Back Squat",
        "Press Pattern": "Bench Press",
        "Row / Pull Pattern": "Chest-Supported Row",
        "Single-Joint Upper": "Cable Curl",
        "Core / Conditioning Finisher": "Ab Wheel",
    },

    "planet_fitness": {
        "Primary Press": "Smith Machine Bench Press",
        "Secondary Press": "Incline Smith Press",
        "Chest Fly": "Pec Deck",
        "Dip / Push-Up Pattern": "Push-Up",
        "Triceps Finisher": "Cable Pressdown",

        "Vertical Pull": "Lat Pulldown",
        "Horizontal Row": "Seated Cable Row",
        "Secondary Row": "Machine Row",
        "Rear Delt / Upper Back": "Reverse Pec Deck",
        "Biceps Finisher": "Cable Curl",

        "Heavy Curl": "Cable Curl",
        "Stretch Curl": "Preacher Curl Machine",
        "Heavy Triceps Press": "Smith Close-Grip Press",
        "Overhead Triceps": "Cable Overhead Extension",
        "Lateral Raise": "Dumbbell Lateral Raise",
        "Forearm / Grip": "Hammer Curl",

        "Primary Squat Pattern": "Smith Machine Squat",
        "Hip Hinge": "Smith Romanian Deadlift",
        "Single-Leg Movement": "Dumbbell Split Squat",
        "Leg Curl Pattern": "Leg Curl Machine",
        "Calf Raise": "Smith Calf Raise",

        "Flat / Main Press": "Smith Machine Bench Press",
        "Overhead Press": "Machine Shoulder Press",
        "Incline Press": "Incline Smith Press",
        "Triceps Pressdown / Extension": "Cable Pressdown",

        "Main Row": "Seated Cable Row",
        "Secondary Pull": "Machine Row",
        "Rear Delt Fly / Face Pull": "Reverse Pec Deck",
        "Curl Variation": "Cable Curl",

        "Horizontal Press": "Smith Bench Press",
        "Vertical Press": "Machine Shoulder Press",
        "Vertical Pull": "Lat Pulldown",
        "Biceps": "Cable Curl",
        "Triceps": "Cable Pressdown",

        "Squat Pattern": "Smith Squat",
        "Press Pattern": "Smith Bench Press",
        "Row / Pull Pattern": "Seated Cable Row",
        "Single-Joint Upper": "Cable Curl",
        "Core / Conditioning Finisher": "Crunch Machine",
    },

    "crunch": {
        "Primary Press": "Barbell Bench Press",
        "Secondary Press": "Incline Dumbbell Press",
        "Chest Fly": "Cable Fly",
        "Dip / Push-Up Pattern": "Weighted Dip",
        "Triceps Finisher": "Rope Pressdown",

        "Vertical Pull": "Pull-Up or Lat Pulldown",
        "Horizontal Row": "Chest-Supported Row",
        "Secondary Row": "Seated Cable Row",
        "Rear Delt / Upper Back": "Face Pull",
        "Biceps Finisher": "EZ-Bar Curl",

        "Heavy Curl": "EZ-Bar Curl",
        "Stretch Curl": "Incline Dumbbell Curl",
        "Heavy Triceps Press": "Close-Grip Bench Press",
        "Overhead Triceps": "Overhead Rope Extension",
        "Lateral Raise": "Dumbbell Lateral Raise",
        "Forearm / Grip": "Hammer Curl",

        "Primary Squat Pattern": "Barbell Back Squat",
        "Hip Hinge": "Romanian Deadlift",
        "Single-Leg Movement": "Bulgarian Split Squat",
        "Leg Curl Pattern": "Seated Leg Curl",
        "Calf Raise": "Standing Calf Raise",

        "Flat / Main Press": "Barbell Bench Press",
        "Overhead Press": "Dumbbell Shoulder Press",
        "Incline Press": "Incline Dumbbell Press",
        "Triceps Pressdown / Extension": "Rope Pressdown",

        "Main Row": "Barbell Row",
        "Secondary Pull": "Cable Row",
        "Rear Delt Fly / Face Pull": "Face Pull",
        "Curl Variation": "EZ-Bar Curl",

        "Horizontal Press": "Bench Press",
        "Vertical Press": "Dumbbell Shoulder Press",
        "Vertical Pull": "Pull-Up or Lat Pulldown",
        "Biceps": "Cable Curl",
        "Triceps": "Rope Pressdown",

        "Squat Pattern": "Back Squat",
        "Press Pattern": "Bench Press",
        "Row / Pull Pattern": "Barbell Row",
        "Single-Joint Upper": "Lateral Raise",
        "Core / Conditioning Finisher": "Cable Crunch",
    },

    "life_time": {
        "Primary Press": "Barbell Bench Press",
        "Secondary Press": "Incline Dumbbell Press",
        "Chest Fly": "Cable Fly",
        "Dip / Push-Up Pattern": "Weighted Dip",
        "Triceps Finisher": "Cable Pressdown",

        "Vertical Pull": "Weighted Pull-Up or Lat Pulldown",
        "Horizontal Row": "Chest-Supported Row",
        "Secondary Row": "Seated Cable Row",
        "Rear Delt / Upper Back": "Face Pull",
        "Biceps Finisher": "EZ-Bar Curl",

        "Heavy Curl": "EZ-Bar Curl",
        "Stretch Curl": "Bayesian Cable Curl",
        "Heavy Triceps Press": "Close-Grip Bench Press",
        "Overhead Triceps": "Cable Overhead Extension",
        "Lateral Raise": "Cable Lateral Raise",
        "Forearm / Grip": "Hammer Curl",

        "Primary Squat Pattern": "High-Bar Back Squat",
        "Hip Hinge": "Romanian Deadlift",
        "Single-Leg Movement": "Walking Lunge",
        "Leg Curl Pattern": "Seated Leg Curl",
        "Calf Raise": "Standing Calf Raise",

        "Flat / Main Press": "Barbell Bench Press",
        "Overhead Press": "Seated Dumbbell Shoulder Press",
        "Incline Press": "Incline Barbell Press",
        "Triceps Pressdown / Extension": "Cable Pressdown",

        "Main Row": "T-Bar Row",
        "Secondary Pull": "Seated Cable Row",
        "Rear Delt Fly / Face Pull": "Face Pull",
        "Curl Variation": "Bayesian Cable Curl",

        "Horizontal Press": "Bench Press",
        "Vertical Press": "Machine Shoulder Press",
        "Vertical Pull": "Weighted Pull-Up or Lat Pulldown",
        "Biceps": "Cable Curl",
        "Triceps": "Cable Pressdown",

        "Squat Pattern": "Back Squat",
        "Press Pattern": "Bench Press",
        "Row / Pull Pattern": "T-Bar Row",
        "Single-Joint Upper": "Cable Lateral Raise",
        "Core / Conditioning Finisher": "Hanging Leg Raise",
    },
}


def build_workout_name(category, gym_type):
    return f"{category.replace('_', ' ').title()} - {GYM_LABELS[gym_type]}"


class Command(BaseCommand):
    help = "Seed default premade workouts for all lifting categories and gym types"

    def handle(self, *args, **kwargs):
        created_count = 0

        for category, payload in BASE_WORKOUTS.items():
            for gym_type, substitutions in EXERCISE_SUBSTITUTIONS.items():
                workout, created = WorkoutTemplate.objects.get_or_create(
                    category=category,
                    gym_type=gym_type,
                    defaults={
                        "name": build_workout_name(category, gym_type),
                        "description": payload["description"],
                    }
                )

                if not created:
                    workout.exercises.all().delete()

                for idx, (placeholder, sets, reps, rest, notes) in enumerate(payload["exercises"], start=1):
                    WorkoutExercise.objects.create(
                        workout=workout,
                        order=idx,
                        name=substitutions.get(placeholder, placeholder),
                        sets=sets,
                        reps=reps,
                        rest_seconds=rest,
                        notes=notes,
                    )

                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {created_count} premade workouts."))