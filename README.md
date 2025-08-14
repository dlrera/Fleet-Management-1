# Fleet Management System

A modern fleet management system built with Django REST Framework backend and Vue.js frontend with Bootstrap styling.

## Tech Stack

- **Backend**: Django 5.0, Django REST Framework
- **Frontend**: Vue 3, Vite, Bootstrap 5
- **Database**: PostgreSQL (production), SQLite (development)
- **State Management**: Pinia
- **HTTP Client**: Axios

## Project Structure

```
fleet-management/
├── backend/            # Django backend
│   ├── apps/          # Django applications
│   ├── config/        # Django settings and configuration
│   └── manage.py      # Django management script
├── frontend/          # Vue.js frontend
│   ├── src/
│   │   ├── assets/    # Static assets and styles
│   │   ├── components/# Vue components
│   │   ├── router/    # Vue Router configuration
│   │   ├── services/  # API services
│   │   ├── store/     # Pinia store
│   │   └── views/     # Vue views/pages
│   └── vite.config.js # Vite configuration
├── requirements.txt   # Python dependencies
└── package.json       # Node.js dependencies
```

## Setup Instructions

### Backend Setup

1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DATABASE_URL=sqlite:///db.sqlite3
   ALLOWED_HOSTS=localhost,127.0.0.1
   CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
   ```

5. Run database migrations:
   ```bash
   cd backend
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the Django development server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. Install Node.js dependencies:
   ```bash
   npm install
   ```

2. Run the Vue development server:
   ```bash
   cd frontend
   npm run dev
   ```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api
- Django Admin: http://localhost:8000/admin

## Development Commands

### Backend
- `python manage.py runserver` - Start development server
- `python manage.py makemigrations` - Create database migrations
- `python manage.py migrate` - Apply database migrations
- `python manage.py test` - Run tests

### Frontend
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

## Features

- Vehicle management
- Driver management
- Maintenance tracking
- Dashboard with key metrics
- RESTful API
- Responsive design with Bootstrap

## License

MIT License - See LICENSE file for details