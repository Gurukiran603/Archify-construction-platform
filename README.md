"# Archify-construction-platform" 
# 🏗️ Archify - Construction Management Platform

[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)

Archify is a comprehensive construction management platform that connects Clients, Architects, Civil Engineers, Contractors, and Workers on a single platform. It streamlines project management, plan approvals, workforce management, and payment processing.

## 🚀 Live Demo
[View Live Site](https://archify-construction-platform.onrender.com) *(after deployment)*

## 📋 Features

### For Clients 👤
- Create and manage construction projects
- Request consultations from professionals
- Track project progress in real-time
- Review and approve building plans
- Leave reviews and ratings

### For Architects 📐
- Upload floor plans, elevations, and 3D renderings
- Version control for design revisions
- Respond to consultation requests
- Get feedback from engineers and clients

### For Civil Engineers 🏗️
- Review structural plans
- Approve or request revisions
- Provide technical comments
- Ensure structural safety compliance

### For Contractors 👷
- Manage worker database
- Assign workers to projects
- Mark daily attendance with check-in/out
- Process wage payments
- Post site updates with photos

### For Workers 🛠️
- View assigned projects
- Track attendance history
- View payment records

### For Admin 👑
- Verify professional profiles
- Manage all users
- Monitor all projects
- Generate reports

## 🛠️ Technology Stack

| Category | Technology |
|----------|------------|
| Backend | Django 5.2 |
| Frontend | Bootstrap 5, HTML5, CSS3 |
| Database | SQLite (Dev) / PostgreSQL (Prod) |
| Authentication | Django Auth with Custom User Model |
| APIs | Django REST Framework |
| File Storage | Local Storage / Cloudinary |
| Deployment | Render.com |

## 📊 Database Models (20+)

- User (Custom with 6 roles)
- ProfessionalProfile
- ClientProfile
- ConstructionProject
- BuildingPlan (with versioning)
- ProjectMilestone
- SiteUpdate
- Worker
- WorkerAttendance
- WagePayment
- Material
- ConsultationRequest
- Notification
- ActivityLog
- PortfolioProject
- ProjectReview

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- pip
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/archify-construction-platform.git
cd archify-construction-platform


Create virtual environment

bash
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
Install dependencies

bash
pip install -r requirements.txt
Configure environment variables
Create .env file:

env
SECRET_KEY=your-secret-key-here
DEBUG=True
Run migrations

bash
python manage.py migrate
Create superuser

bash
python manage.py createsuperuser
Load sample data (optional)

bash
python manage.py shell < populate_data.py
Run development server

bash
python manage.py runserver
Open browser

text
http://127.0.0.1:8000
👥 Default Login Credentials
Role	Username	Password
Client	client	client123
Architect	architect	arch123
Civil Engineer	engineer	eng123
Contractor	contractor	cont123
Worker	worker	worker123
Admin	admin	admin123
📁 Project Structure
text
archify/
├── base/
│   ├── migrations/
│   ├── templates/
│   │   ├── base/
│   │   ├── dashboard/
│   │   ├── projects/
│   │   ├── workers/
│   │   ├── attendance/
│   │   ├── consultations/
│   │   └── materials/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── myproject/
│   ├── settings.py
│   └── urls.py
├── static/
├── media/
├── manage.py
└── requirements.txt
🔧 Deployment on Render
Push code to GitHub

Create account on render.com

Connect GitHub repository

Configure build settings:

Build Command: ./build.sh

Start Command: gunicorn myproject.wsgi:application

Add environment variables

Deploy

🎯 Key Workflows
Project Creation Workflow
Client registers and creates project

Client requests consultation from architect

Architect responds and accepts project

Architect uploads building plans

Civil engineer reviews structural plans

Contractor assigns workers

Contractor marks daily attendance

Client approves and reviews

Attendance & Payment Workflow
Contractor adds workers to system

Contractor assigns workers to project

Daily attendance marked (Present/Absent/Half Day)

Monthly wage calculated automatically

Contractor processes payments

Worker views payment history

📈 Future Enhancements
Mobile app for workers

Payment gateway integration

GPS-based worker tracking

AI-based material estimation

Real-time chat system

Video consultation support

Drone site imagery integration

🤝 Contributing
Fork the repository

Create feature branch (git checkout -b feature/AmazingFeature)

Commit changes (git commit -m 'Add AmazingFeature')

Push to branch (git push origin feature/AmazingFeature)

Open Pull Request

📄 License
This project is licensed under the MIT License.

👨‍💻 Author
Gurukiran C S

GitHub: @yourusername

LinkedIn: Your Name

🙏 Acknowledgments
Django Community

Bootstrap Team

All contributors

📞 Support
For support, email support@archify.com or open an issue on GitHub.

⭐ Star us on GitHub — it helps!
Made with ❤️ for Construction Professionals

text

---

## Step 3: Create `.gitignore` File

Create `.gitignore` in your project root:

```gitignore
# Python
__pycache__/
*.py[cod]
*.so
.Python
env/
venv/
myenv/
ENV/
env.bak/
venv.bak/
*.egg-info/
dist/
build/

# Django
*.log
*.pot
*.pyc
db.sqlite3
db.sqlite3-journal
media/
staticfiles/
static/

# Environment
.env
.env.local
.env.production

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store
Thumbs.db

# Testing
.coverage
htmlcov/
.pytest_cache/

# Deployment
*.pid
*.seed
*.pid.lock

# Logs
logs/
*.log

# Local settings
local_settings.py
