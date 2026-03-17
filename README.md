# Workout App

A secure, full-stack web application designed for comprehensive fitness and nutrition tracking. This project was developed as part of the **Software Engineering** curriculum at the **College of the Holy Cross**.

## 👥 Project Team
Developed by Brian Rippy and Brenden Gruburg, two undergraduate computer science students at the College of the Holy Cross.

---

## 📖 Project Overview
The **Workout App** provides a streamlined interface for users to manage their fitness journeys. Built with the Django framework, the application utilizes a **Login-First** architecture to protect user data and provide personalized tracking for workouts and nutritional goals.

### Key Features
* **Authentication Gate:** Strict root-level login requirements with advanced password complexity validation (8+ characters and special character enforcement).
* **User Profile Integration:** Custom onboarding flow for recording physical metrics, including height (ft/in), current weight, goal weight, and target timelines.
* **Workout Management:** Dynamic routing for multiple fitness categories, including Lifting, Cardio, Sports, and Mobility.
* **Gym Customization:** Integrated setup options allowing users to tailor workouts based on available equipment (Bodyweight, Home Gym, or Commercial Gym).

---

## 🛠 Technical Stack
* **Backend:** Python 3.x, Django
* **Database:** SQLite3
* **Frontend:** HTML5, CSS3, Django Template Language
* **Security:** Django Authentication System with custom `RegexValidator` for password integrity.

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Workout_App
```

### 2. Environment Setup
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install django
```

### 3. Database Initialization
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Run the Development Server
```bash
python manage.py runserver
```
Access the application at `http://127.0.0.1:8000/`.

---

## 🏗 System Architecture
The project follows the **Model-View-Template (MVT)** pattern:
* **Models:** Utilizes a `Profile` model linked via a One-to-One relationship to the Django `User` to store fitness-specific metrics.
* **Forms:** Features a custom `SignUpForm` that overrides the default `save()` method to handle unit conversions and data mapping between the UI and the database.
* **URL Routing:** Centralized routing ensures all application features are namespaced under `/tracker/` for security and organization.

---

## 🏛 Academic Context
* **Institution:** College of the Holy Cross
* **Department:** Computer Science
* **Course:** Software Engineering (CSCI 399)

---

**Would you like me to create a "Technical Challenges" section for the README that explains how you solved the naming mismatch between the signup form and the database?**
