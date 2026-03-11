from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(label="Name", required=True)
    
    # Input fields for the signup screen
    height_ft = forms.IntegerField(label="Height (ft)", min_value=4, max_value=7)
    height_in = forms.IntegerField(label="Height (in)", min_value=0, max_value=11)
    weight_lbs = forms.IntegerField(label="Current Weight (lbs)")
    goal_weight_lbs = forms.IntegerField(label="Goal Weight (lbs)")
    
    TIMELINE_CHOICES = [
        ('3m', '3 Months'),
        ('6m', '6 Months'),
        ('1y', '1 Year'),
        ('2y', '2 Years'),
    ]
    timeline = forms.ChoiceField(choices=TIMELINE_CHOICES, label="Goal Timeline")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name',)

    def save(self, commit=True):
        # 1. Save the base User (this handles the password hashing)
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        
        if commit:
            user.save()
            
            # 2. Combine the ft/in inputs into the string the model expects
            h_ft = self.cleaned_data['height_ft']
            h_in = self.cleaned_data['height_in']
            height_string = f"{h_ft}'{h_in}\""
            
            # 3. Create the Profile and MAP the names correctly
            # Form field 'weight_lbs' -> Model field 'weight'
            Profile.objects.create(
                user=user,
                height=height_string,
                weight=self.cleaned_data['weight_lbs'],
                goal_weight=self.cleaned_data['goal_weight_lbs'],
                timeline=self.cleaned_data['timeline']
            )
        return user