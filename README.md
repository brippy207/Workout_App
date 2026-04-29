# Workout App

A full-stack Django web application for managing workouts, tracking nutrition, and monitoring fitness progress. This project centralizes workout planning, macro tracking, and performance analytics into a single interface.

## Overview

Workout App is built using Django’s Model-View-Template (MVT) architecture. It allows users to log workouts, track daily nutrition, set macro goals, and visualize progress over time. The application integrates external APIs for enhanced functionality, including food search and optional AI-based food estimation.

## Features

### Authentication & User Management
- Secure user registration and login
- Session-based authentication
- User-specific data (workouts, nutrition, stats)

### Workout System
- Predefined workout routines
- Custom workout creation
- Saved workouts management
- Categorized workout navigation

### Nutrition Tracking
- Manual food entry with macro tracking (protein, carbs, fats)
- Adjustable daily macro goals
- Real-time calorie and macro progress visualization
- Food search via FatSecret API
- Optional AI-based food estimation from images (Google Gemini)

### Statistics
- Workout history tracking
- Weight logging
- Progress visualization

## Technology Stack

- **Backend:** Django (Python 3.12)
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite (default)
- **APIs:**
  - FatSecret API (food search)
  - Google Gemini API (optional image analysis)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/brippy207/Workout_App.git
cd Workout_App


2. Create and Activate Virtual Environment

Windows

python -m venv venv
venv\Scripts\activate

macOS/Linux

python3 -m venv venv
source venv/bin/activate
3. Install Dependencies

If requirements.txt exists:

pip install -r requirements.txt

If not, install manually:

pip install django requests google-generativeai

Then generate:

pip freeze > requirements.txt
Environment Configuration

Create a .env file or define environment variables:

SECRET_KEY=your_django_secret_key

FATSECRET_CLIENT_ID=your_client_id
FATSECRET_CLIENT_SECRET=your_client_secret

GEMINI_API_KEY=your_gemini_api_key

Update settings.py to read from environment variables:

import os

SECRET_KEY = os.getenv("SECRET_KEY")
Database Setup

Run migrations:

python manage.py makemigrations
python manage.py migrate

(Optional) Seed initial workout data:

python manage.py seed_workouts
Running the Application

Start the development server:

python manage.py runserver

Access the application:

http://127.0.0.1:8000/
Project Structure
Workout_App/
│
├── Workout_App/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── tracker/
│   ├── templates/tracker/
│   │   ├── nutrition.html
│   │   ├── workouts.html
│   │   ├── stats.html
│   │   └── ...
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── management/commands/
│
├── static/
├── templates/
├── manage.py
└── README.md
API Setup
FatSecret API

Used for food search functionality.

Register at: https://platform.fatsecret.com/
Create an application
Add credentials to environment variables
Google Gemini API (Optional)

Used for AI-based food image analysis.

Install dependency:

pip install google-generativeai

If not using this feature, remove or comment out related imports and views.

Security Considerations
Do not commit API keys or secrets
Use environment variables for all sensitive data
Regenerate any keys previously exposed
Ensure .env, venv/, and db.sqlite3 are in .gitignore
Set DEBUG=False in production
Known Issues
Missing API keys will break food search and AI features
SQLite is not recommended for production
Nutrition page depends on correct context data from views
License

This project is licensed under the MIT License.


---

### Hidden Bugs (More Precise Pass)

These are not guesses — these are actual structural issues:

---

#### 1. **Critical: nutrition.html expects data that may not exist**
Your template uses:
```js
document.getElementById('food-data')