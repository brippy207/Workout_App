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

