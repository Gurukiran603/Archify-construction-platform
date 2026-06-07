# 🏗️ Archify - Construction Management Platform

[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)

Archify is a comprehensive construction management platform that connects Clients, Architects, Civil Engineers, Contractors, and Workers on a single platform. It streamlines project management, plan approvals, workforce management, and payment processing.

## 🚀 Live Demo
[View Live Site](https://archify.onrender.com) *(after deployment)*

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