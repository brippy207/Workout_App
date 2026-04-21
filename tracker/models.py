from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Stores formatted string like 5'11"
    height = models.CharField(max_length=10) 
    # Stores values in lbs
    weight = models.IntegerField() 
    goal_weight = models.IntegerField()
    # Stores timeline choice
    timeline = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    

class WorkoutLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_name = models.CharField(max_length=100) # "Run", "Swim", etc.
    distance = models.FloatField(null=True, blank=True) # Miles
    duration = models.IntegerField(null=True, blank=True) # Minutes
    date = models.DateField(default=timezone.localdate)
    # This stores the Google Calendar-style colors
    color = models.CharField(max_length=20, default="#e67e22") 

class WeightEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    weight = models.IntegerField()
    date = models.DateField(default=timezone.localdate)

    class Meta:
        ordering = ['date']

class FoodLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_name = models.CharField(max_length=200)
    protein = models.FloatField()
    carbs = models.FloatField()
    fats = models.FloatField()
    date = models.DateField(default=timezone.localdate)

    class Meta:
        ordering = ['-date']

class CustomLiftWorkout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_lift_workouts')
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        unique_together = ('user', 'name')

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class CustomLiftExercise(models.Model):
    workout = models.ForeignKey(CustomLiftWorkout, on_delete=models.CASCADE, related_name='exercises')
    exercise_name = models.CharField(max_length=120)
    default_sets = models.PositiveIntegerField()
    default_reps = models.PositiveIntegerField()
    default_weight = models.FloatField()

    def __str__(self):
        return f"{self.workout.name} - {self.exercise_name}"


class LiftExerciseLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lift_logs')
    workout = models.ForeignKey(CustomLiftWorkout, on_delete=models.CASCADE, related_name='lift_logs')
    exercise = models.ForeignKey(CustomLiftExercise, on_delete=models.CASCADE, related_name='exercise_logs')
    sets = models.PositiveIntegerField()
    reps = models.PositiveIntegerField()
    weight = models.FloatField()
    date = models.DateField(default=timezone.localdate)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.user.username} - {self.exercise.exercise_name} - {self.date}"
    
class UserGoal(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    protein_goal = models.IntegerField(default=150)
    carb_goal = models.IntegerField(default=200)
    fat_goal = models.IntegerField(default=70)

    def __str__(self):
        return f"{self.user.username}'s Goals"

