from django.db import models
from django.contrib.auth.models import User

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