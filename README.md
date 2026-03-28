<div align="center">
  <h1>SevenSteps 🎯</h1>
  <p>AI-powered goal achievement app that breaks your goals into actionable 7-day plans.</p>

[![Python](https://img.shields.io/badge/Python-3.12-3777A7?style=flat-square)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-103E2E?style=flat-square)](https://www.djangoproject.com/)
[![Vue](https://img.shields.io/badge/Vue-3-42b883?style=flat-square)](https://vuejs.org/)
[![DRF](https://img.shields.io/badge/DRF-3.16-7F2D2D?style=flat-square)](https://www.django-rest-framework.org/)
[![Pytest](https://img.shields.io/badge/Pytest-Passed-2dad3f?style=flat-square)](https://docs.pytest.org/)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-4285F4?style=flat-square)](https://deepmind.google/technologies/gemini/)

  <img src="https://github.com/user-attachments/assets/0c4fe906-b9a7-4c2f-95ba-2b5da645fdaf" style="width: 80%;"/>
</div>

---

# 📖 Table of Contents

<ul>
  <li><b><a href="#-description">Description</a></b></li>
  <li><b><a href="#-demonstration">Demonstration</a></b></li>
  <li><b><a href="#-features">Features</a></b></li>
  <li><b><a href="#-tech-stack">Tech Stack</a></b></li>
  <li><b><a href="#-local-installation">Local Installation</a></b></li>
  <li><b><a href="#-deployment">Deployment</a></b></li>
  <li><b><a href="#-testing">Testing</a></b></li>
</ul>

---

<details open><summary><h1>📃 Description</h1></summary>

**SevenSteps** is a full-stack web application that combines a to-do list with AI. You enter your goal — the app generates a personalized **7-day action plan** using **Google Gemini AI**. Each day becomes a task you can complete, track on a calendar, and manage through your profile.

The app supports **two languages** (English and Russian), **JWT authentication**, **Google OAuth**, and **transactional email** for account management actions like password reset and email change.

API documentation is available at [`/api/docs/`](https://sevensteps-0fvn.onrender.com/api/docs/).

</details>

> [!NOTE]
> This project was created for educational purposes as a portfolio project.

🌐 **Live Demo:** [https://sevensteps-frontend.onrender.com](https://sevensteps-frontend.onrender.com)

---

<details><summary><h1>🌄 Demonstration</h1></summary>

### Today — Task List

<img src="https://github.com/user-attachments/assets/0c4fe906-b9a7-4c2f-95ba-2b5da645fdaf" style="width: 49%;"/>

### Create Plan

<img src="https://github.com/user-attachments/assets/0737df6a-af40-4825-a846-ac7de1519c4d" style="width: 49%;"/>

### Calendar

<img src="https://github.com/user-attachments/assets/5c557eaf-832a-43b3-9589-8df539fbd796" style="width: 49%;"/>
<img src="https://github.com/user-attachments/assets/5c9dc8da-ca7b-4235-abeb-20271981ad2e" style="width: 49%;"/>

### Profile

<img src="https://github.com/user-attachments/assets/78373428-a3c8-4d96-9c0b-58e86f4e0e74" style="width: 49%;"/>

### Settings

<img src="https://github.com/user-attachments/assets/66667789-bbf1-43c3-b911-6bdd537d559a" style="width: 49%;"/>
<img src="https://github.com/user-attachments/assets/811c995d-f354-4cd8-832b-5c50f7ecef9c" style="width: 49%;"/>
<img src="https://github.com/user-attachments/assets/8016f207-7e5d-41f5-9d3b-b56a7f721e1b" style="width: 49%;"/>

### Authorization

<img src="https://github.com/user-attachments/assets/3e75a31d-d75f-4fac-964a-43dd5e763223" style="width: 49%;"/>
<img src="https://github.com/user-attachments/assets/e5bf03cc-3eb0-4c71-bc9d-d4183345f566" style="width: 49%;"/>

</details>

---

<details><summary><h1>🔥 Features</h1></summary>

- **AI Plan Generation** — Enter any goal and get a 7-day step-by-step plan powered by Google Gemini
- **JWT Authentication** — Secure login with access/refresh token rotation and blacklisting
- **Google OAuth** — Sign in with Google account
- **Password Reset** — Reset password via email code
- **Email Change** — Change account email with verification code and cancellation link
- **Calendar View** — Visual task calendar to track daily progress
- **Bilingual Interface** — Full English and Russian language support
- **Brute-force Protection** — Login attempt limiting via django-axes
- **Transactional Email** — Emails via Resend API
- **API Documentation** — Interactive docs via Swagger UI
- **Tests** — Backend covered with PyTest

</details>

---

<details><summary><h1>⚙️ Tech Stack</h1></summary>

**Backend**
- Python 3.12 / Django 5 / Django REST Framework
- PostgreSQL
- JWT Authentication (SimpleJWT)
- Google Gemini 2.5 Flash API
- Resend (transactional email)
- Docker / Gunicorn
- django-axes (brute-force protection)
- drf-spectacular (API docs)
- PyTest

**Frontend**
- Vue 3 (Composition API)
- Vue Router
- Axios
- vue-i18n (internationalization)
- Vite
- SCSS

**Infrastructure**
- Render (backend as Docker web service, frontend as static site)
- UptimeRobot (uptime monitoring)

</details>

---

<details><summary><h1>💽 Local Installation</h1></summary>

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL

### Backend

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file in the backend root:
   ```env
   SECRET_KEY=your-secret-key
   DATABASE_URL=postgres://user:password@localhost:5432/sevensteps
   GEMINI_API_KEY=your-gemini-api-key
   FRONTEND_URL=http://localhost:5173
   GOOGLE_OAUTH2_KEY=your-google-oauth-key
   ADMIN_URL=admin
   EMAIL_HOST_USER=your-email@gmail.com
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   ```

   > For local development, emails are printed to the console — no real email service needed.

5. Apply migrations and run:
   ```bash
   python manage.py migrate
   python manage.py createcachetable
   python manage.py runserver
   ```

### Frontend

1. Go to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create `.env` file:
   ```env
   VITE_API_URL=http://localhost:8000/api/
   ```

4. Run the dev server:
   ```bash
   npm run dev
   ```

</details>

---

<details><summary><h1>🐳 Deployment</h1></summary>

The project is deployed on **Render** using Docker for the backend and static site hosting for the frontend.

### Backend (Web Service)

1. Connect your GitHub repository to Render
2. Select **Docker** as the environment
3. Add environment variables in Render dashboard:

   ```
   SECRET_KEY=
   DATABASE_URL=
   GEMINI_API_KEY=
   FRONTEND_URL=
   GOOGLE_OAUTH2_KEY=
   ADMIN_URL=
   RESEND_API_KEY=
   DEFAULT_FROM_EMAIL=
   ALLOWED_HOSTS=
   CORS_ALLOWED_ORIGINS=
   CSRF_TRUSTED_ORIGINS=
   DJANGO_SETTINGS_MODULE=config.settings.production
   ```

### Frontend (Static Site)

1. Add a new **Static Site** on Render
2. Set build command: `npm run build`
3. Set publish directory: `dist`
4. Add environment variable:
   ```
   VITE_API_URL=https://your-backend.onrender.com/api/
   ```

### Email (Resend)

1. Register at [resend.com](https://resend.com)
2. Add and verify your domain in Resend → Domains
3. Add the DNS records provided by Resend to your domain registrar
4. Set `RESEND_API_KEY` and `DEFAULT_FROM_EMAIL` in Render environment variables

### Keep-Alive (UptimeRobot)

Render free tier spins down inactive services after 15 minutes. To prevent this:

1. Register at [uptimerobot.com](https://uptimerobot.com)
2. Create an HTTP monitor for `https://your-backend.onrender.com/health/`
3. Set interval to **5 minutes**

</details>

---

<details><summary><h1>⚒️ Testing</h1></summary>

1. Complete all steps in the Local Installation section
2. Run tests:
   ```bash
   cd backend
   pytest
   ```

</details>