# Workout App

A full-stack Django web application for managing workouts, tracking nutrition, and monitoring fitness progress. This project centralizes workout planning, macro tracking, and performance analytics into a single interface.

---

## Overview

Workout App is built using Django’s Model-View-Template (MVT) architecture. It allows users to log workouts, track daily nutrition, set macro goals, and visualize progress over time. The application integrates external APIs for enhanced functionality, including food search and optional AI-based food estimation.

---

## Features

### Authentication & User Management
- Secure user registration and login
- Session-based authentication
- User-specific data storage

### Workout System
- Predefined workout routines
- Custom workout creation
- Saved workouts management
- Categorized workout navigation

### Nutrition Tracking
- Manual food entry (protein, carbs, fats)
- Adjustable daily macro goals
- Real-time calorie and macro progress bars
- Food search via FatSecret API
- Optional AI-based food estimation (Google Gemini)

### Statistics
- Workout history tracking
- Weight logging
- Progress visualization

---

## Technology Stack

- **Backend:** Django (Python 3.12)
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite (default)
- **APIs:**
  - FatSecret API (food search)
  - Google Gemini API (optional image analysis)

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/brippy207/Workout_App.git
cd Workout_App
````

### 2. Create and Activate Virtual Environment

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

If `requirements.txt` exists:

```bash
pip install -r requirements.txt
```

If not:

```bash
pip install django requests google-generativeai
pip freeze > requirements.txt
```

---

## Environment Configuration

Create a `.env` file or set environment variables:

```env
SECRET_KEY=your_django_secret_key
FATSECRET_CLIENT_ID=your_client_id
FATSECRET_CLIENT_SECRET=your_client_secret
GEMINI_API_KEY=your_gemini_api_key
```

---

## Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

(Optional)

```bash
python manage.py seed_workouts
```

---

## Run the Application

```bash
python manage.py runserver
```

Open in browser:

```
http://127.0.0.1:8000/
```

---

## Project Structure

```
Workout_App/
│
├── Workout_App/
│   ├── settings.py
│   └── urls.py
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
```

---

## API Setup

### FatSecret API

* Sign up at: [https://platform.fatsecret.com/](https://platform.fatsecret.com/)
* Create an app and obtain credentials
* Add them to environment variables

### Google Gemini API (Optional)

```bash
pip install google-generativeai
```

If not using AI features, you may remove the related code.

---

## Security Notes

* Do not commit API keys to GitHub
* Use environment variables for sensitive data
* Add `.env`, `venv/`, and `db.sqlite3` to `.gitignore`
* Set `DEBUG=False` in production

---

## License

This project is licensed under the MIT License.
