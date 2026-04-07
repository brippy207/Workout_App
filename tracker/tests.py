import json
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import FoodLog, Profile, WeightEntry


class TrackerViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="tester",
            password="secret123",
            first_name="Taylor",
        )
        self.profile = Profile.objects.create(
            user=self.user,
            height="5'11\"",
            weight=210,
            goal_weight=180,
            timeline="6m",
        )
        self.client.login(username="tester", password="secret123")

    def test_stats_uses_logged_weights_without_duplicate_start_point(self):
        start_date = timezone.localdate() - timedelta(days=3)
        WeightEntry.objects.create(user=self.user, weight=210, date=start_date)
        WeightEntry.objects.create(user=self.user, weight=205, date=start_date + timedelta(days=3))

        response = self.client.get(reverse("stats"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["labels_json"], [0, 3])
        self.assertEqual(response.context["values_json"], [210.0, 205.0])
        self.assertEqual(response.context["current_weight"], 205.0)

    def test_stats_falls_back_to_profile_weight_when_no_entries_exist(self):
        response = self.client.get(reverse("stats"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["labels_json"], [0])
        self.assertEqual(response.context["values_json"], [210.0])
        self.assertEqual(response.context["current_weight"], 210.0)

    def test_log_weight_ignores_invalid_input(self):
        response = self.client.post(reverse("log_weight"), {"weight": "abc"})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(WeightEntry.objects.filter(user=self.user).count(), 0)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.weight, 210)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), "Enter a valid weight greater than 0.")

    def test_log_food_ignores_invalid_macros(self):
        response = self.client.post(
            reverse("log_food"),
            {
                "food_name": "Greek Yogurt",
                "protein": "bad",
                "carbs": "10",
                "fats": "0",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(FoodLog.objects.filter(user=self.user).count(), 0)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), "Enter a food name and valid macro values.")

    def test_log_food_ajax_returns_validation_message(self):
        response = self.client.post(
            reverse("log_food"),
            {
                "food_name": "",
                "protein": "10",
                "carbs": "20",
                "fats": "5",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {"ok": False, "message": "Enter a food name and valid macro values."},
        )

    def test_search_food_requires_login(self):
        self.client.logout()

        response = self.client.post(
            reverse("search_food"),
            data=json.dumps({"query": "banana"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
